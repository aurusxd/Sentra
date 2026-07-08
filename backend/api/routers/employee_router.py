from fastapi import APIRouter, Depends

from backend.utils.depends import provider
from backend.database.models.user import User
from backend.schemas.employee_schema import EmployeeCreate, EmployeeRead, EmployeeUpdate
from backend.services.employee_service import EmployeeService
from backend.core.security import get_current_user

router = APIRouter(prefix="/employees", tags=["Employees"])

employee_service = EmployeeService()


@router.get("/", response_model=list[EmployeeRead])
async def get_employees(
    current_user: User = Depends(get_current_user),
):
    return await employee_service.get_all(owner_id=current_user.id)


@router.post("/", response_model=EmployeeRead)
async def create_employee(
    data: EmployeeCreate,
    current_user: User = Depends(get_current_user),
):
    return await employee_service.create(
        owner_id=current_user.id,
        data=data,
    )


@router.get("/{employee_id}", response_model=EmployeeRead)
async def get_employee(
    employee_id: int,
    current_user: User = Depends(get_current_user),
):
    return await employee_service.get_by_id(
        employee_id=employee_id,
        owner_id=current_user.id,
    )


@router.patch("/{employee_id}", response_model=EmployeeRead)
async def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    current_user: User = Depends(get_current_user),
):
    return await employee_service.update(
        employee_id=employee_id,
        owner_id=current_user.id,
        data=data,
    )


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    current_user: User = Depends(get_current_user),
):
    return await employee_service.delete(
        employee_id=employee_id,
        owner_id=current_user.id,
    )