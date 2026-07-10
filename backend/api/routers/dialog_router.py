from fastapi import APIRouter, Depends, HTTPException, status

from backend.database.enums import DialogStatus
from backend.database.models.user import User
from backend.core.security import get_current_user
from backend.schemas.dialog_schema import DialogRead, HumanMessageCreate, MessageRead
from backend.services.dialog_service import dialog_service
from backend.services.employee_service import employee_service
from backend.services.message_service import message_service
from backend.services.telegram_service import TelegramService
from backend.utils.toeken_crypto import decrypt_token

router = APIRouter(prefix="/dialog", tags=["Dialog"])
telegram_service = TelegramService()


async def ensure_dialog_owner(dialog_id: int, current_user: User):
    dialog = await dialog_service.get_by_id(dialog_id=dialog_id)
    await employee_service.get_by_id(
        employee_id=dialog.employee_id,
        owner_id=current_user.id,
    )
    return dialog


@router.get("/", response_model=list[DialogRead])
async def get_dialogs(
    employee_id: int,
    current_user: User = Depends(get_current_user),
):
    await employee_service.get_by_id(
        employee_id=employee_id,
        owner_id=current_user.id,
    )

    dialogs = await dialog_service.get_by_employee_id(
        employee_id=employee_id
    )

    return dialogs


@router.get("/{dialog_id}", response_model=DialogRead)
async def get_dialog(
    dialog_id: int,
    current_user: User = Depends(get_current_user),
):
    return await ensure_dialog_owner(
        dialog_id=dialog_id,
        current_user=current_user,
    )


@router.post("/{dialog_id}/takeover", response_model=DialogRead)
async def takeover_dialog(
    dialog_id: int,
    current_user: User = Depends(get_current_user),
):
    await ensure_dialog_owner(
        dialog_id=dialog_id,
        current_user=current_user,
    )
    await dialog_service.takeover(dialog_id=dialog_id)
    return await dialog_service.get_by_id(dialog_id=dialog_id)


@router.post("/{dialog_id}/return", response_model=DialogRead)
async def return_dialog_to_employee(
    dialog_id: int,
    current_user: User = Depends(get_current_user),
):
    await ensure_dialog_owner(
        dialog_id=dialog_id,
        current_user=current_user,
    )
    await dialog_service.return_to_employee(dialog_id=dialog_id)
    return await dialog_service.get_by_id(dialog_id=dialog_id)


@router.post("/{dialog_id}/resolve", response_model=DialogRead)
async def resolve_dialog(
    dialog_id: int,
    current_user: User = Depends(get_current_user),
):
    await ensure_dialog_owner(
        dialog_id=dialog_id,
        current_user=current_user,
    )
    await dialog_service.resolve(dialog_id=dialog_id)
    return await dialog_service.get_by_id(dialog_id=dialog_id)


@router.post("/{dialog_id}/messages", response_model=MessageRead)
async def send_human_message(
    dialog_id: int,
    data: HumanMessageCreate,
    current_user: User = Depends(get_current_user),
):
    text = data.text.strip()

    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message text is required",
        )

    dialog = await ensure_dialog_owner(
        dialog_id=dialog_id,
        current_user=current_user,
    )

    if dialog.channel is None or dialog.channel.token_encrypted is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dialog channel is not connected",
        )

    token = decrypt_token(dialog.channel.token_encrypted)
    telegram_message = await telegram_service.send_message(
        token=token,
        chat_id=dialog.client_external_id,
        text=text,
    )

    message_id = telegram_message.get("message_id")

    if dialog.status != DialogStatus.NEEDS_HUMAN or not dialog.is_human_takeover:
        await dialog_service.takeover(dialog_id=dialog_id)

    return await message_service.create_human_message(
        dialog_id=dialog_id,
        text=text,
        external_message_id=str(message_id) if message_id is not None else None,
    )


