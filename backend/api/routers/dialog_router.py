from fastapi import APIRouter, Depends

from backend.database.models.dialog import Dialog
from backend.utils.depends import provider
from backend.database.models.user import User
from backend.schemas.employee_schema import EmployeeCreate, EmployeeRead, EmployeeUpdate
from backend.services.employee_service import EmployeeService
from backend.core.security import get_current_user
from backend.services.dialog_service import dialog_service

router = APIRouter(prefix="/dialog", tags=["Dialog"])


@router.get("/",response_model=list[Dialog])
async def get_dialogs(
    employee_id: int,
) -> list[Dialog]:
    dialogs = await dialog_service.get_by_employee_id(
        employee_id=employee_id
    )

    return dialogs




