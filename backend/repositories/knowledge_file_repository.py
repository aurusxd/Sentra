from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.utils.depends import provider
from backend.database.models.knowledge_file import KnowledgeFile


class KnowledgeFileRepository:
    @provider.inject_session
    async def get_all_by_employee(
        self,
        employee_id: int,
        session: AsyncSession,
    ) -> list[KnowledgeFile]:
        result = await session.execute(
            select(KnowledgeFile).where(
                KnowledgeFile.employee_id == employee_id,
            )
        )

        return list(result.scalars().all())

    @provider.inject_session
    async def get_by_id(
        self,
        file_id: int,
        employee_id: int,
        session: AsyncSession,
    ) -> KnowledgeFile | None:
        result = await session.execute(
            select(KnowledgeFile).where(
                KnowledgeFile.id == file_id,
                KnowledgeFile.employee_id == employee_id,
            )
        )

        return result.scalar_one_or_none()

    @provider.inject_session
    async def create(
        self,
        file: KnowledgeFile,
        session: AsyncSession,
    ) -> KnowledgeFile:
        session.add(file)
        await session.flush()
        await session.refresh(file)

        return file

    @provider.inject_session
    async def update(
        self,
        file: KnowledgeFile,
        session: AsyncSession,
    ) -> KnowledgeFile:
        session.add(file)
        await session.flush()
        await session.refresh(file)

        return file

    @provider.inject_session
    async def delete(
        self,
        file: KnowledgeFile,
        session: AsyncSession,
    ) -> None:
        await session.delete(file)
        await session.flush()