import httpx
from fastapi import HTTPException, status
from backend.config import API_URL


class TelegramService:
    def __init__(self):
        self.api_url = "https://api.telegram.org/bot"

    def _build_url(self, token: str, method: str) -> str:
        return f"{self.api_url}{token}/{method}"

    async def get_me(self, token: str) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                self._build_url(token, "getMe")
            )

        data = response.json()

        if not data.get("ok"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Telegram bot token",
            )

        return data["result"]

    async def set_webhook(
        self,
        token: str,
        webhook_secret: str,
        header_secret: str,
    ) -> bool:
        webhook_url = f"{API_URL}/telegram/webhook/{webhook_secret}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                self._build_url(token, "setWebhook"),
                json={
                    "url": webhook_url,
                    "secret_token": header_secret,
                },
            )

        data = response.json()

        if not data.get("ok"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to set Telegram webhook",
            )

        return True

    async def delete_webhook(self, token: str) -> bool:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                self._build_url(token, "deleteWebhook"),
            )

        data = response.json()

        if not data.get("ok"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete Telegram webhook",
            )

        return True

    async def send_message(
        self,
        token: str,
        chat_id: int | str,
        text: str,
    ) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                self._build_url(token, "sendMessage"),
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                },
            )

        try:
            data = response.json()
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Telegram API returned HTTP {response.status_code} with an invalid response",
            ) from error

        if not data.get("ok"):
            description = data.get("description", "Unknown Telegram API error")
            error_code = data.get("error_code", response.status_code)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Telegram API error {error_code}: {description}",
            )

        return data["result"]
