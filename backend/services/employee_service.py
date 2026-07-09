from fastapi import HTTPException, status

from backend.database.models.employee import Employee
from backend.repositories.employee_repository import EmployeeRepository
from backend.schemas.employee_schema import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    def __init__(self):
        self.repository = EmployeeRepository()

    async def get_all(self, owner_id: int):
        return await self.repository.get_all(owner_id=owner_id)

    async def get_by_id(self, employee_id: int, owner_id: int):
        employee = await self.repository.get_by_id(
            employee_id=employee_id,
            owner_id=owner_id,
        )

        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found",
            )

        return employee

    async def create(self, owner_id: int, data: EmployeeCreate):
        employee = Employee(
            owner_id=owner_id,
            status="active",
            **data.model_dump(),
        )

        return await self.repository.create(employee=employee)

    async def update(
        self,
        employee_id: int,
        owner_id: int,
        data: EmployeeUpdate,
    ):
        employee = await self.get_by_id(
            employee_id=employee_id,
            owner_id=owner_id,
        )

        values = data.model_dump(exclude_unset=True)

        for key, value in values.items():
            setattr(employee, key, value)

        return await self.repository.update(employee=employee)

    async def delete(self, employee_id: int, owner_id: int):
        employee = await self.get_by_id(
            employee_id=employee_id,
            owner_id=owner_id,
        )
        employee.is_deleted = True
        return await self.repository.update(employee=employee)
    

    async def get_by_id_for_webhook(self, employee_id: int):
        employee = await self.repository.get_by_id_only(
            employee_id=employee_id,
        )

        if employee is None:
            raise HTTPException(
                status_code=404,
                detail="Employee not found",
            )

        return employee

employee_service = EmployeeService()
