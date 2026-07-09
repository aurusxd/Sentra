import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from backend.database.models.knowledge_file import KnowledgeFile
from backend.repositories.knowledge_file_repository import KnowledgeFileRepository
from backend.services.loader_service import loader_service
from backend.services.embedding_service import EmbeddingService

UPLOAD_DIR = Path("uploads/knowledge")
embedding_service = EmbeddingService()

class KnowledgeFileService:
    def __init__(self):
        self.repository = KnowledgeFileRepository()

    async def get_all_by_employee(self, employee_id: int):
        return await self.repository.get_all_by_employee(
            employee_id=employee_id,
        )

    async def get_by_id(self, file_id: int, employee_id: int):
        file = await self.repository.get_by_id(
            file_id=file_id,
            employee_id=employee_id,
        )

        if file is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge file not found",
            )

        return file

    async def upload(
        self,
        employee_id: int,
        upload_file: UploadFile,
    ) -> KnowledgeFile:
        if upload_file.filename is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File name is required",
            )

        allowed_extensions = {".pdf", ".docx", ".txt"}

        original_filename = upload_file.filename
        extension = Path(original_filename).suffix.lower()

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF, DOCX and TXT files are allowed",
            )

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        stored_filename = f"{uuid4().hex}{extension}"
        file_path = UPLOAD_DIR / stored_filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

        size_bytes = file_path.stat().st_size

        knowledge_file = KnowledgeFile(
            employee_id=employee_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            mime_type=upload_file.content_type,
            size_bytes=size_bytes,
            status="uploaded",
        )

        file = await self.repository.create(file=knowledge_file)
        chunks = await loader_service.document_loader(doc=file,employee_id=employee_id)
        embedding_service.add_chunks(
            employee_id=employee_id,
            knowledge_file_id=file.id,
            document_name=file.original_filename,
            chunks=chunks
        )
        return file

    async def mark_processing(
        self,
        file_id: int,
        employee_id: int,
    ) -> KnowledgeFile:
        file = await self.get_by_id(
            file_id=file_id,
            employee_id=employee_id,
        )

        file.status = "processing"

        return await self.repository.update(file=file)

    async def mark_ready(
        self,
        file_id: int,
        employee_id: int,
    ) -> KnowledgeFile:
        file = await self.get_by_id(
            file_id=file_id,
            employee_id=employee_id,
        )

        file.status = "ready"
        file.error_message = None

        return await self.repository.update(file=file)

    async def mark_error(
        self,
        file_id: int,
        employee_id: int,
        error_message: str,
    ) -> KnowledgeFile:
        file = await self.get_by_id(
            file_id=file_id,
            employee_id=employee_id,
        )

        file.status = "error"
        file.error_message = error_message

        return await self.repository.update(file=file)

    async def delete(
        self,
        file_id: int,
        employee_id: int,
    ) -> dict:
        file = await self.get_by_id(
            file_id=file_id,
            employee_id=employee_id,
        )

        file_path = Path(file.file_path)

        if file_path.exists():
            file_path.unlink()

        await self.repository.delete(file=file)

        return {"message": "Knowledge file deleted"}
    
knowledge_service = KnowledgeFileService()