import hmac
from html import escape

from fastapi import APIRouter, Depends, Header, HTTPException, status

from backend.database.enums import ChannelStatus, ChannelType, EmployeeStatus
from backend.services.agent_service import ask_agent
from backend.services.channel_service import ChannelService
from backend.services.dialog_service import dialog_service
from backend.services.employee_service import employee_service
from backend.services.max_service import MaxService
from backend.services.message_service import message_service
from backend.services.vector_store_service import vector_store_service
from backend.utils.logger import log
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
        "🔴 Требуется помощь оператора\n\n"
        f"AI-сотрудник: {escape(employee_name)}\n"
        f"Клиент: {escape(format_max_client_name(sender))}\n"
        f"Username: {escape(formatted_username)}\n"
        f"MAX chat ID: {escape(str(chat_id))}\n\n"
        "Сообщение:\n"
        f"{escape(text)}"
    )


async def notify_max_admin_about_fallback(
    token: str,
    admin_chat_id: str | None,
    employee_name: str,
    sender: dict,
    chat_id: int | str,
    text: str,
) -> None:
    if not admin_chat_id:
        log.warning("MAX admin chat id is not set")
        return

    try:
        await max_service.send_message(
            token=token,
            chat_id=admin_chat_id,
            text=build_max_operator_help_message(
                employee_name=employee_name,
                sender=sender,
                chat_id=chat_id,
                text=text,
            ),
        )
    except Exception:
        log.exception("MAX admin fallback notification was not sent")


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

    if update.get("update_type") != "message_created":
        return {"success": True}

    message = update.get("message") or {}
    sender = message.get("sender") or {}
    recipient = message.get("recipient") or {}
    body = message.get("body") or {}
    text = body.get("text")
    chat_id = recipient.get("chat_id")
    sender_id = sender.get("user_id")
    external_message_id = body.get("mid")

    if sender.get("is_bot") or not text or chat_id is None or sender_id is None:
        return {"success": True}

    await enforce_rate_limit(
        scope=f"max-chat:{channel.id}",
        key_value=str(chat_id),
        limit=20,
        window_seconds=60,
    )

    dialog = await dialog_service.get_or_create(
        employee_id=channel.employee_id,
        channel_id=channel.id,
        client_external_id=str(chat_id),
        client_name=format_max_client_name(sender),
        client_username=sender.get("username"),
    )
    if dialog is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Dialog not created")

    if external_message_id and await message_service.client_message_exists(dialog.id, str(external_message_id)):
        log.info("Duplicate MAX message ignored for dialog {}", dialog.id)
        return {"success": True}

    await message_service.create_client_message(
        dialog_id=dialog.id,
        text=text,
        external_message_id=str(external_message_id) if external_message_id else None,
    )

    if dialog.is_human_takeover:
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

    token = decrypt_token(channel.token_encrypted)
    max_answer = await max_service.send_message(
        token=token,
        chat_id=chat_id,
        text=answer,
    )
    if handoff_required:
        await dialog_service.mark_needs_human(dialog_id=dialog.id)
        await notify_max_admin_about_fallback(
            token=token,
            admin_chat_id=employee.max_admin_chat_id,
            employee_name=employee.name,
            sender=sender,
            chat_id=chat_id,
            text=text,
        )

    answer_body = max_answer.get("body") or {}
    await message_service.create_employee_message(
        dialog_id=dialog.id,
        text=answer,
        external_message_id=str(answer_body.get("mid")) if answer_body.get("mid") else None,
    )

    log.success("MAX answer sent for dialog {}", dialog.id)
    return {"success": True}
