from fastapi import APIRouter, Depends, HTTPException, status

from backend.core.security import get_current_user
from backend.database.enums import ChannelStatus, EmployeeStatus
from backend.database.models.user import User
from backend.services.agent_service import ask_agent
from backend.services.channel_service import ChannelService
from backend.services.dialog_service import dialog_service
from backend.services.employee_service import employee_service
from backend.services.message_service import message_service
from backend.services.telegram_service import TelegramService
from backend.services.vector_store_service import vector_store_service
from backend.utils.toeken_crypto import decrypt_token
from backend.utils.logger import log

router = APIRouter(
    prefix="/telegram",
    tags=["Telegram Webhook"],
)

channel_service = ChannelService()
telegram_service = TelegramService()


@router.post("/webhook/{webhook_secret}")
async def telegram_webhook(
    webhook_secret: str,
    update: dict,
):
    channel = await channel_service.get_by_webhook_secret(
        webhook_secret=webhook_secret,
    )

    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found",
        )

    if channel.status != ChannelStatus.CONNECTED:
        log.error("Channel is not connected")
        return {"ok": True}

    employee = await employee_service.get_by_id_for_webhook(
        employee_id=channel.employee_id,
    )

    if employee.is_deleted or employee.status != EmployeeStatus.ACTIVE:
        log.error("Employee is deleted or employee status is not active")
        return {"ok": True}
    message = update.get("message")
    if not message:
        log.error("Message not taked")
        return {"ok": True}

    text = message.get("text")
    chat = message.get("chat", {})
    chat_id = chat.get("id")

    if not text or not chat_id:
        log.error("Unable to get text or chat_id")
        return {"ok": True}

    dialog = await dialog_service.get_or_create(
        employee_id=channel.employee_id,
        channel_id=channel.id,
        client_external_id=str(chat_id),
        client_name=chat.get("first_name"),
        client_username=chat.get("username"),
    )

    if dialog is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dialog not created",
        )

    msg = await message_service.create_client_message(
        dialog_id=dialog.id,
        text=text,
        external_message_id=str(message.get("message_id")),
    )
    if msg is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Message not created",
        )

    token = decrypt_token(channel.token_encrypted)

    found_chunks = await vector_store_service.find_vectors(
        employee_id=channel.employee_id,
        question=text,
    )
    message_context = "\n\n".join(chunk.page_content for chunk in found_chunks)

    answer = await ask_agent(
        question=text,
        post=employee.role,
        description=employee.business_description,
        instruction=employee.instruction,
        tone=employee.tone,
        context=message_context,
        fallback=employee.fallback_message,
    )

    if answer is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Answer not taked",
        )
    await telegram_service.send_message(
        token=token,
        chat_id=chat_id,
        text=answer,
    )

    employee_msg = await message_service.create_employee_message(
        dialog_id=dialog.id,
        text=answer,
        external_message_id=str(message.get("message_id")),
    )
    if employee_msg is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Employee message not created",
        )

    log.success(f"All its fine, answe:{answer}")
    return {"ok": True}
