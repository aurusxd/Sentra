from pathlib import Path
from uuid import uuid4
from zipfile import BadZipFile, ZipFile

import pymupdf

from fastapi import HTTPException, UploadFile, status

from backend.database.models.knowledge_file import KnowledgeFile
from backend.repositories.knowledge_file_repository import KnowledgeFileRepository
from backend.services.loader_service import loader_service
from backend.services.embedding_service import EmbeddingService

UPLOAD_DIR = Path("uploads/knowledge")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_DOCX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024
MAX_PDF_PAGES = 500
embedding_service = EmbeddingService()


def validate_uploaded_file(path: Path, extension: str) -> None:
    if extension == ".pdf":
        if not path.read_bytes()[:5].startswith(b"%PDF-"):
            raise ValueError("Invalid PDF signature")
        with pymupdf.open(path) as document:
            if document.page_count > MAX_PDF_PAGES:
                raise ValueError(f"PDF cannot contain more than {MAX_PDF_PAGES} pages")
    elif extension == ".docx":
        try:
            with ZipFile(path) as archive:
                names = set(archive.namelist())
                if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                    raise ValueError("Invalid DOCX structure")
                total_uncompressed = sum(item.file_size for item in archive.infolist())
                if total_uncompressed > MAX_DOCX_UNCOMPRESSED_BYTES:
                    raise ValueError("DOCX archive is too large after decompression")
                for item in archive.infolist():
                    if item.compress_size and item.file_size / item.compress_size > 100:
                        raise ValueError("Suspicious DOCX compression ratio")
        except BadZipFile as error:
            raise ValueError("Invalid DOCX archive") from error
    else:
        path.read_text(encoding="utf-8")

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
        existing_files = await self.repository.get_all_by_employee(employee_id=employee_id)
        if len(existing_files) >= 50:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Knowledge file limit reached",
            )

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

        size_bytes = 0
        try:
            with file_path.open("wb") as buffer:
                while chunk := await upload_file.read(1024 * 1024):
                    size_bytes += len(chunk)
                    if size_bytes > MAX_UPLOAD_BYTES:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail="File cannot exceed 10 MB",
                        )
                    buffer.write(chunk)

            validate_uploaded_file(file_path, extension)
        except HTTPException:
            file_path.unlink(missing_ok=True)
            raise
        except (OSError, UnicodeError, ValueError) as error:
            file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error) or "Invalid document",
            ) from error
        finally:
            await upload_file.close()

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
        return await self.process(file=file, employee_id=employee_id)

    async def process(
        self,
        file: KnowledgeFile,
        employee_id: int,
    ) -> KnowledgeFile:
        """Index a knowledge file and always persist its terminal status."""
        file.status = "processing"
        file.error_message = None
        await self.repository.update(file=file)

        try:
            chunks = await loader_service.document_loader(
                doc=file,
                employee_id=employee_id,
            )
            indexed = await embedding_service.add_chunks(
                employee_id=employee_id,
                knowledge_file_id=file.id,
                document_name=file.original_filename,
                chunks=chunks,
            )
            if not indexed:
                raise RuntimeError("Document indexing failed")
        except Exception as error:
            return await self.mark_error(
                file_id=file.id,
                employee_id=employee_id,
                error_message=str(error) or "Document indexing failed",
            )

        return await self.mark_ready(
            file_id=file.id,
            employee_id=employee_id,
        )

    async def reindex(
        self,
        file_id: int,
        employee_id: int,
    ) -> KnowledgeFile:
        file = await self.get_by_id(
            file_id=file_id,
            employee_id=employee_id,
        )
        return await self.process(file=file, employee_id=employee_id)

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
