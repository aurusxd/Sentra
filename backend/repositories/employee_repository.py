from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database.enums import DialogStatus
from backend.database.models.dialog import Dialog
from backend.utils.depends import provider
from backend.database.models.employee import Employee


class EmployeeRepository:
    @staticmethod
    def _dashboard_query():
        dialogs = (
            select(func.count(Dialog.id))
            .where(Dialog.employee_id == Employee.id)
            .correlate(Employee)
            .scalar_subquery()
        )
        active_dialogs = (
            select(func.count(Dialog.id))
            .where(
                Dialog.employee_id == Employee.id,
                Dialog.status != DialogStatus.RESOLVED,
            )
            .correlate(Employee)
            .scalar_subquery()
        )
        human_pending = (
            select(func.count(Dialog.id))
            .where(
                Dialog.employee_id == Employee.id,
                Dialog.status == DialogStatus.NEEDS_HUMAN,
            )
            .correlate(Employee)
            .scalar_subquery()
        )
        return (
            select(
                Employee,
                dialogs.label("dialogs_count"),
                active_dialogs.label("active_dialogs_count"),
                human_pending.label("human_pending_count"),
            )
            .options(selectinload(Employee.channels))
        )

    @staticmethod
    def _apply_dashboard_state(rows) -> list[Employee]:
        employees = []
        for employee, dialogs, active_dialogs, human_pending in rows:
            employee.set_dialog_counts(
                total=int(dialogs or 0),
                active=int(active_dialogs or 0),
                human_pending=int(human_pending or 0),
            )
            employees.append(employee)
        return employees

    @provider.inject_session
    async def get_all(
        self,
        owner_id: int,
        session: AsyncSession,
    ) -> list[Employee]:
        result = await session.execute(
            self._dashboard_query().where(
                Employee.owner_id == owner_id,
                Employee.is_deleted.is_(False),
            )
        )
        return self._apply_dashboard_state(result.all())

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
            self._dashboard_query().where(
                Employee.id == employee_id,
                Employee.owner_id == owner_id,
                Employee.is_deleted.is_(False),
            )
        )
        employees = self._apply_dashboard_state(result.all())
        return employees[0] if employees else None

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
