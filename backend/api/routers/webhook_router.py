from fastapi import APIRouter, HTTPException, status

from backend.services.channel_service import ChannelService
from backend.services.telegram_service import TelegramService
from backend.utils.toeken_crypto import decrypt_token

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

    message = update.get("message")

    if not message:
        return {"ok": True}

    text = message.get("text")
    chat = message.get("chat", {})
    chat_id = chat.get("id")

    if not text or not chat_id:
        return {"ok": True}

    token = decrypt_token(channel.token_encrypted)

    # временный ответ, чтобы проверить webhook
    answer = f"Сообщение получил: {text}"

    await telegram_service.send_message(
        token=token,
        chat_id=chat_id,
        text=answer,
    )

    return {"ok": True}