from typing import Any

import httpx
from fastapi import HTTPException, status

from backend.config import API_URL


class MaxService:
    def __init__(self) -> None:
        self.api_url = "https://platform-api2.max.ru"
        self.timeout = 10.0

    def _build_url(self, method: str) -> str:
        return f"{self.api_url}/{method.lstrip('/')}"

    @staticmethod
    def _headers(token: str) -> dict[str, str]:
        return {"Authorization": token}

    async def _request(
        self,
        method: str,
        endpoint: str,
        token: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        invalid_token_is_bad_request: bool = False,
    ) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method,
                    self._build_url(endpoint),
                    headers=self._headers(token),
                    params=params,
                    json=json,
                )
        except httpx.RequestError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"MAX API request failed: {error}",
            ) from error

        try:
            data = response.json()
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"MAX API returned HTTP {response.status_code} with an invalid response",
            ) from error

        if not isinstance(data, dict):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="MAX API returned an invalid response object",
            )

        if response.is_error:
            detail = data.get("message") or data.get("error") or response.reason_phrase
            response_status = (
                status.HTTP_400_BAD_REQUEST
                if invalid_token_is_bad_request
                and response.status_code
                in (
                    status.HTTP_400_BAD_REQUEST,
                    status.HTTP_401_UNAUTHORIZED,
                    status.HTTP_403_FORBIDDEN,
                )
                else status.HTTP_502_BAD_GATEWAY
            )
            raise HTTPException(
                status_code=response_status,
                detail=f"MAX API error {response.status_code}: {detail}",
            )

        return data

    async def get_me(self, token: str) -> dict[str, Any]:
        return await self._request(
            "GET",
            "me",
            token,
            invalid_token_is_bad_request=True,
        )

    async def set_webhook(
        self,
        token: str,
        webhook_secret: str,
        header_secret: str,
    ) -> bool:
        webhook_url = f"{str(API_URL).rstrip('/')}/max/webhook/{webhook_secret}"
        data = await self._request(
            "POST",
            "subscriptions",
            token,
            json={
                "url": webhook_url,
                "update_types": ["message_created", "bot_started"],
                "secret": header_secret,
            },
        )

        if not data.get("success"):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to set MAX webhook: {data.get('message', 'unknown MAX API error')}",
            )

        return True

    async def delete_webhook(self, token: str, webhook_secret: str) -> bool:
        webhook_url = f"{str(API_URL).rstrip('/')}/max/webhook/{webhook_secret}"
        result = await self._request(
            "DELETE",
            "subscriptions",
            token,
            params={"url": webhook_url},
        )
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to delete MAX webhook: {result.get('message', 'unknown MAX API error')}",
            )

        return True

    async def send_message(
        self,
        token: str,
        chat_id: int | str,
        text: str,
    ) -> dict[str, Any]:
        data = await self._request(
            "POST",
            "messages",
            token,
            params={"chat_id": chat_id},
            json={
                "text": text,
                "format": "html",
            },
        )

        message = data.get("message")
        if not isinstance(message, dict):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="MAX API returned an invalid message response",
            )

        return message
