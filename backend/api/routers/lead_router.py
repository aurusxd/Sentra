from html import escape

from fastapi import APIRouter, Depends, HTTPException, status

from backend.config import TELEGRAM_LEAD_BOT_TOKEN, TELEGRAM_LEAD_CHAT_ID
from backend.schemas.lead_schema import LeadCreate, LeadResponse
from backend.services.telegram_service import TelegramService
from backend.utils.logger import log
from backend.utils.rate_limit import rate_limit

router = APIRouter(prefix="/leads", tags=["Leads"])
telegram_service = TelegramService()


@router.post("", response_model=LeadResponse, dependencies=[Depends(rate_limit("leads", 5, 60))])
async def create_lead(data: LeadCreate) -> LeadResponse:
    # Honeypot field for basic protection from automated form spam.
    if data.website.strip():
        return LeadResponse(ok=True)

    if not TELEGRAM_LEAD_BOT_TOKEN or not TELEGRAM_LEAD_CHAT_ID:
        log.error("Telegram lead notifications are not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис заявок временно недоступен",
        )

    text = "\n".join(
        (
            "🚀 <b>Новая заявка на запуск Sentra</b>",
            "",
            f"<b>Имя:</b> {escape(data.name.strip())}",
            f"<b>Телефон:</b> {escape(data.phone.strip())}",
            f"<b>Telegram:</b> {escape(data.telegram.strip())}",
        )
    )

    try:
        await telegram_service.send_message(
            token=TELEGRAM_LEAD_BOT_TOKEN,
            chat_id=TELEGRAM_LEAD_CHAT_ID,
            text=text,
        )
    except HTTPException as error:
        log.error("Failed to send lead notification to Telegram: {}", error.detail)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Не удалось отправить заявку",
        ) from error

    return LeadResponse(ok=True)
