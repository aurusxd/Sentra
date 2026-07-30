import hmac
from html import escape

from fastapi import APIRouter, Depends, Header, HTTPException, status

from backend.database.enums import ChannelStatus, ChannelType, DialogStatus, EmployeeStatus
from backend.services.agent_service import ask_agent
from backend.services.channel_service import ChannelService
from backend.services.dialog_service import dialog_service
from backend.services.employee_service import employee_service
from backend.services.max_service import MaxService
from backend.services.message_service import message_service
from backend.services.vector_store_service import vector_store_service
from backend.utils.logger import log
from backend.utils.max_operator_callback import (
    create_max_operator_callback,
    parse_max_operator_callback,
)
from backend.utils.rate_limit import enforce_rate_limit, rate_limit
from backend.utils.telegram_webhook_auth import telegram_webhook_header_secret
from backend.utils.toeken_crypto import decrypt_token

router = APIRouter(prefix="/max", tags=["MAX Webhook"])
channel_service = ChannelService()
max_service = MaxService()


def format_max_client_name(sender: dict) -> str:
    first_name = sender.get("first_name") or ""
    last_name = sender.get("last_name") or ""
    return f"{first_name} {last_name}".strip() or sender.get("name") or "Неизвестно"


def build_max_operator_help_message(
    employee_name: str,
    sender: dict,
    chat_id: int | str,
    text: str,
) -> str:
    username = sender.get("username")
    formatted_username = (
        f"@{username}" if username and not username.startswith("@") else username or "-"
    )
    return (
        "🔴 <b>Нужен оператор</b>\n\n"
        f"AI-сотрудник: {escape(employee_name)}\n"
        f"Клиент: {escape(format_max_client_name(sender))}\n"
        f"Username: {escape(formatted_username)}\n"
        f"MAX chat ID: {escape(str(chat_id))}\n\n"
        f"Вопрос: {escape(text)}"
    )


def build_operator_keyboard(dialog_id: int) -> list[dict]:
    return [
        {
            "type": "inline_keyboard",
            "payload": {
                "buttons": [
                    [
                        {
                            "type": "callback",
                            "text": "Взять диалог",
                            "payload": create_max_operator_callback("take", dialog_id),
                            "intent": "positive",
                        },
                        {
                            "type": "callback",
                            "text": "Закрыть",
                            "payload": create_max_operator_callback("close", dialog_id),
                            "intent": "negative",
                        },
                    ]
                ]
            },
        }
    ]


def get_message_id(message: dict) -> str | None:
    message_id = (message.get("body") or {}).get("mid")
    return str(message_id) if message_id else None


def get_reply_message_id(message: dict) -> str | None:
    link = message.get("link") or {}
    reply_id = link.get("mid")
    if not reply_id:
        linked_message = link.get("message") or {}
        reply_id = linked_message.get("mid")
        if not reply_id:
            reply_id = (linked_message.get("body") or {}).get("mid")
    return str(reply_id) if reply_id else None


async def notify_max_admin_about_fallback(
    token: str,
    admin_chat_id: str | None,
    dialog_id: int,
    employee_name: str,
    sender: dict,
    client_chat_id: int | str,
    text: str,
) -> None:
    if not admin_chat_id:
        log.warning("MAX admin chat id is not set")
        return

    try:
        notification = await max_service.send_message(
            token=token,
            chat_id=admin_chat_id,
            text=build_max_operator_help_message(
                employee_name=employee_name,
                sender=sender,
                chat_id=client_chat_id,
                text=text,
            ),
            attachments=build_operator_keyboard(dialog_id),
        )
        notification_id = get_message_id(notification)
        if notification_id:
            await dialog_service.save_max_admin_notification(
                dialog_id=dialog_id,
                message_id=notification_id,
            )
    except Exception:
        log.exception("MAX admin fallback notification was not sent")


async def send_operator_status(token: str, admin_chat_id: str, text: str) -> None:
    await max_service.send_message(token=token, chat_id=admin_chat_id, text=text)


async def handle_operator_callback(
    update: dict,
    channel,
    employee,
    token: str,
) -> dict:
    callback = update.get("callback") or {}
    callback_id = callback.get("callback_id")
    parsed = parse_max_operator_callback(str(callback.get("payload") or ""))
    callback_message = callback.get("message") or {}
    admin_chat_id = update.get("chat_id")
    if admin_chat_id is None:
        admin_chat_id = (callback_message.get("recipient") or {}).get("chat_id")
    admin_user_id = (callback.get("user") or {}).get("user_id")

    if not callback_id or not parsed:
        log.warning("Invalid MAX operator callback payload")
        return {"success": True}
    if (
        admin_chat_id is None
        or admin_user_id is None
        or not employee.max_admin_chat_id
        or str(admin_chat_id) != str(employee.max_admin_chat_id)
    ):
        await max_service.answer_callback(token, str(callback_id), "Недостаточно прав")
        return {"success": True}

    action, dialog_id = parsed
    dialog = await dialog_service.get_by_id(dialog_id=dialog_id)
    if dialog.channel_id != channel.id or dialog.employee_id != employee.id:
        await max_service.answer_callback(token, str(callback_id), "Диалог не найден")
        return {"success": True}

    if action == "take":
        await dialog_service.start_max_operator_session(
            dialog_id=dialog.id,
            channel_id=channel.id,
            admin_chat_id=str(admin_chat_id),
            admin_user_id=str(admin_user_id),
        )
        await max_service.answer_callback(token, str(callback_id), "Диалог принят")
        await send_operator_status(
            token,
            str(admin_chat_id),
            f"✅ Диалог с {escape(dialog.client_name or 'клиентом')} принят. Пишите сообщения сюда. /готово — завершить, /отмена — вернуть AI.",
        )
    else:
        await dialog_service.stop_max_operator_session(dialog.id, resolved=True)
        await max_service.answer_callback(token, str(callback_id), "Диалог закрыт")

    return {"success": True}


async def handle_admin_message(
    message: dict,
    channel,
    token: str,
    admin_chat_id: str,
    sender_id: int | str,
    text: str,
) -> dict:
    dialog = None
    reply_message_id = get_reply_message_id(message)
    if reply_message_id:
        dialog = await dialog_service.get_by_max_admin_notification(
            channel_id=channel.id,
            message_id=reply_message_id,
        )
        if dialog:
            dialog = await dialog_service.start_max_operator_session(
                dialog_id=dialog.id,
                channel_id=channel.id,
                admin_chat_id=admin_chat_id,
                admin_user_id=str(sender_id),
            )

    if dialog is None:
        dialog = await dialog_service.get_active_max_operator_dialog(
            channel_id=channel.id,
            admin_chat_id=admin_chat_id,
        )

    if dialog is None:
        await send_operator_status(
            token,
            admin_chat_id,
            "Сначала нажмите «Взять диалог» или ответьте на уведомление о клиенте.",
        )
        return {"success": True}

    if dialog.max_operator_user_id and str(dialog.max_operator_user_id) != str(sender_id):
        await send_operator_status(token, admin_chat_id, "Этот диалог взят другим оператором.")
        return {"success": True}

    command = text.strip().lower()
    if command == "/готово":
        await dialog_service.stop_max_operator_session(dialog.id, resolved=True)
        await send_operator_status(token, admin_chat_id, "✅ Диалог завершён. Следующее сообщение клиента снова обработает AI.")
        return {"success": True}
    if command == "/отмена":
        await dialog_service.stop_max_operator_session(dialog.id)
        await send_operator_status(token, admin_chat_id, "↩️ Управление диалогом возвращено AI.")
        return {"success": True}

    external_message_id = get_message_id(message)
    if external_message_id and await message_service.human_message_exists(dialog.id, external_message_id):
        return {"success": True}

    sent_message = await max_service.send_message(
        token=token,
        chat_id=dialog.client_external_id,
        text=escape(text),
    )
    await message_service.create_human_message(
        dialog_id=dialog.id,
        text=text,
        external_message_id=external_message_id or get_message_id(sent_message),
    )
    return {"success": True}


@router.post(
    "/webhook/{webhook_secret}",
    dependencies=[Depends(rate_limit("max-webhook", 600, 60))],
)
async def max_webhook(
    webhook_secret: str,
    update: dict,
    max_secret: str | None = Header(default=None, alias="X-Max-Bot-Api-Secret"),
):
    channel = await channel_service.get_by_webhook_secret(webhook_secret=webhook_secret)
    if channel is None or channel.type != ChannelType.MAX:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MAX channel not found")

    expected_secret = telegram_webhook_header_secret(webhook_secret)
    if not max_secret or not hmac.compare_digest(max_secret, expected_secret):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid MAX webhook secret")
    if channel.status != ChannelStatus.CONNECTED:
        return {"success": True}

    employee = await employee_service.get_by_id_for_webhook(employee_id=channel.employee_id)
    if employee.is_deleted or employee.status != EmployeeStatus.ACTIVE:
        return {"success": True}

    token = decrypt_token(channel.token_encrypted)
    if update.get("update_type") == "message_callback":
        return await handle_operator_callback(update, channel, employee, token)
    if update.get("update_type") != "message_created":
        return {"success": True}

    message = update.get("message") or {}
    sender = message.get("sender") or {}
    recipient = message.get("recipient") or {}
    body = message.get("body") or {}
    text = body.get("text")
    chat_id = recipient.get("chat_id")
    sender_id = sender.get("user_id")
    external_message_id = get_message_id(message)

    if sender.get("is_bot") or not text or chat_id is None or sender_id is None:
        return {"success": True}

    await enforce_rate_limit(
        scope=f"max-chat:{channel.id}",
        key_value=str(chat_id),
        limit=20,
        window_seconds=60,
    )

    if employee.max_admin_chat_id and str(chat_id) == str(employee.max_admin_chat_id):
        return await handle_admin_message(
            message=message,
            channel=channel,
            token=token,
            admin_chat_id=str(chat_id),
            sender_id=sender_id,
            text=text,
        )

    dialog = await dialog_service.get_or_create(
        employee_id=channel.employee_id,
        channel_id=channel.id,
        client_external_id=str(chat_id),
        client_name=format_max_client_name(sender),
        client_username=sender.get("username"),
    )
    if dialog.status == DialogStatus.RESOLVED:
        dialog = await dialog_service.return_to_employee(dialog.id)

    if external_message_id and await message_service.client_message_exists(dialog.id, external_message_id):
        log.info("Duplicate MAX message ignored for dialog {}", dialog.id)
        return {"success": True}

    await message_service.create_client_message(
        dialog_id=dialog.id,
        text=text,
        external_message_id=external_message_id,
    )

    if dialog.is_human_takeover and dialog.max_operator_chat_id:
        await max_service.send_message(
            token=token,
            chat_id=dialog.max_operator_chat_id,
            text=f"<b>{escape(dialog.client_name or 'Клиент')}:</b> {escape(text)}",
            reply_to_message_id=dialog.max_admin_notification_message_id,
        )
        return {"success": True}

    if dialog.status == DialogStatus.NEEDS_HUMAN:
        await notify_max_admin_about_fallback(
            token=token,
            admin_chat_id=employee.max_admin_chat_id,
            dialog_id=dialog.id,
            employee_name=employee.name,
            sender=sender,
            client_chat_id=chat_id,
            text=text,
        )
        return {"success": True}

    found_chunks = await vector_store_service.find_vectors(
        employee_id=channel.employee_id,
        question=text,
    )
    agent_response = await ask_agent(
        question=text,
        post=employee.role,
        description=employee.business_description,
        instruction=employee.instruction,
        tone=employee.tone,
        context="\n\n".join(chunk.page_content for chunk in found_chunks),
    )
    if agent_response is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Answer not created")

    handoff_required = agent_response["status"] == "handoff"
    answer = employee.fallback_message if handoff_required else agent_response.get("answer")
    if not answer:
        answer = employee.fallback_message
        handoff_required = True

    max_answer = await max_service.send_message(token=token, chat_id=chat_id, text=answer)
    if handoff_required:
        await dialog_service.mark_needs_human(dialog_id=dialog.id)
        await notify_max_admin_about_fallback(
            token=token,
            admin_chat_id=employee.max_admin_chat_id,
            dialog_id=dialog.id,
            employee_name=employee.name,
            sender=sender,
            client_chat_id=chat_id,
            text=text,
        )

    await message_service.create_employee_message(
        dialog_id=dialog.id,
        text=answer,
        external_message_id=get_message_id(max_answer),
    )
    log.success("MAX answer sent for dialog {}", dialog.id)
    return {"success": True}
