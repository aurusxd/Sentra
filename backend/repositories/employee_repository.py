from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.utils.depends import provider
from backend.database.models.employee import Employee


class EmployeeRepository:
    @provider.inject_session
    async def get_all(
        self,
        owner_id: int,
        session: AsyncSession,
    ) -> list[Employee]:
        result = await session.execute(
            select(Employee).where(
                Employee.owner_id == owner_id,
                Employee.is_deleted.is_(False),
            )
        )
        return list(result.scalars().all())

    @provider.inject_session
    async def get_by_id_only(
        self,
        employee_id: int,
        session: AsyncSession,
        ) -> Employee | None:
            result = await session.execute(
                 select(Employee).where(
                      Employee.id == employee_id,
                      Employee.is_deleted.is_(False),
                 )
            )
            return result.scalar_one_or_none()


    @provider.inject_session
    async def get_by_id(
        self,
        employee_id: int,
        owner_id: int,
        session: AsyncSession,
    ) -> Employee | None:
        result = await session.execute(
            select(Employee).where(
                Employee.id == employee_id,
                Employee.owner_id == owner_id,
                Employee.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    @provider.inject_session
    async def create(
        self,
        employee: Employee,
        session: AsyncSession,
    ) -> Employee:
        session.add(employee)
        await session.flush()
        await session.refresh(employee)
        return employee

    @provider.inject_session
    async def update(
        self,
        employee: Employee,
        session: AsyncSession,
    ) -> Employee:
        session.add(employee)
        await session.flush()
        await session.refresh(employee)
        return employee

    @provider.inject_session
    async def delete(
        self,
        employee: Employee,
        session: AsyncSession,
    ) -> Employee:
        session.add(employee)
        await session.flush()
        await session.refresh(employee)
        return employee
