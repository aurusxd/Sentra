from fastapi import APIRouter, Depends, HTTPException, status

from backend.core.security import get_current_user
from backend.database.models.user import User
from backend.database.enums import ChannelType
from backend.schemas.channel_schema import ChannelConnect, ChannelRead, MaxConnectionStatus
from backend.services.channel_service import ChannelService
from backend.services.employee_service import EmployeeService
from backend.services.max_service import MaxService
from backend.utils.toeken_crypto import decrypt_token
from backend.utils.telegram_webhook_auth import telegram_webhook_header_secret

router = APIRouter(
    prefix="/employees/{employee_id}/max",
    tags=["MAX"],
)

employee_service = EmployeeService()
channel_service = ChannelService()
max_service = MaxService()


@router.post(
    "/connect",
    response_model=ChannelRead,
    status_code=status.HTTP_201_CREATED,
)
async def connect_max(
    employee_id: int,
    data: ChannelConnect,
    current_user: User = Depends(get_current_user),
):
    await employee_service.get_by_id(
        employee_id=employee_id,
        owner_id=current_user.id,
    )

    if data.type != ChannelType.MAX:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Channel type must be max",
        )

    bot_info = await max_service.get_me(token=data.token)

    channel = await channel_service.create(
        data=data,
        employee_id=employee_id,
        bot_id=bot_info["user_id"],
        bot_username=bot_info.get("username"),
    )

    await max_service.set_webhook(
        token=data.token,
        webhook_secret=channel.webhook_secret,
        header_secret=telegram_webhook_header_secret(channel.webhook_secret),
    )

    return channel


@router.get(
    "/check",
    response_model=MaxConnectionStatus,
)
async def check_max(
    employee_id: int,
    current_user: User = Depends(get_current_user),
):
    await employee_service.get_by_id(
        employee_id=employee_id,
        owner_id=current_user.id,
    )

    channel = await channel_service.get_max_by_employee_id(
        employee_id=employee_id,
    )

    if channel is None:
        return {
            "connected": False,
            "bot_name": None,
            "bot_username": None,
            "status": "disconnected",
        }

    token = decrypt_token(channel.token_encrypted)

    bot_info = await max_service.get_me(token=token)

    connected = channel.status == "connected"

    return {
        "connected": connected,
        "bot_name": bot_info.get("first_name") or bot_info.get("name"),
        "bot_username": bot_info.get("username"),
        "status": channel.status,
    }


@router.delete(
    "/disconnect",
    response_model=ChannelRead,
)
async def disconnect_max(
    employee_id: int,
    current_user: User = Depends(get_current_user),
):
    await employee_service.get_by_id(
        employee_id=employee_id,
        owner_id=current_user.id,
    )

    channel = await channel_service.get_max_by_employee_id(
        employee_id=employee_id,
    )

    if channel is not None and channel.token_encrypted:
        token = decrypt_token(channel.token_encrypted)
        await max_service.delete_webhook(
            token=token,
            webhook_secret=channel.webhook_secret,
        )

    return await channel_service.disconnect(
        employee_id=employee_id,
        channel_type=ChannelType.MAX,
    )
