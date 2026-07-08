from datetime import datetime
import unicodedata
from backend.utils.depends import provider
from anyio import Path as anyioPath
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyMuPDFLoader,
    TextLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.database.models.knowledge_file import KnowledgeFile
from backend.database.models.document_chunk import DocumentChunk
from backend.utils.logger import log
from backend.utils.depends import AsyncSession

class DocumentLoader:
    @provider.inject_session
    async def document_loader(
        self, doc: KnowledgeFile, employee_id: int, session: AsyncSession
    ) -> list[KnowledgeFile]:
        """
        Принимает документ айди и возвращает чанки документа.

        Возвращает: чанки документа

        """
        try:    
            raw_path = doc.file_path

            clean_path = "".join(
                ch for ch in raw_path if unicodedata.category(ch) != "Cf"
            ).strip()

            path = anyioPath(clean_path)

            if not await path.exists():
                msg = f"Файл не найден: {str(path)!r}"
                raise FileNotFoundError(msg)

            match path.suffix:
                case ".pdf":
                    log.info("Получил pdf файл")
                    loader = PyMuPDFLoader(str(path))
                case ".txt":
                    log.info("Получил txt файл")
                    loader = TextLoader(str(path), encoding="utf-8")
                case ".docx":
                    log.info("Получил docx файл")
                    loader = Docx2txtLoader(str(path))

            docs = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=700,
                chunk_overlap=50,
            )

            chunks = text_splitter.split_documents(docs)
            for i, c in enumerate(chunks):
                doc_chunk = DocumentChunk(
                    knowledge_file_id=doc.id,
                    employee_id=employee_id,
                    chunk_index=i + 1,
                    text=c.page_content,
                    created_at=datetime.now(),
                )
                session.add(doc_chunk)
                await session.flush()
                await session.refresh(doc_chunk)

            log.info(f"Документ загружен и разбит на {len(chunks)} чанков")

            return chunks

        except Exception:
            log.exception("Ошибка при загрузке документа")
            raise


loader_service = DocumentLoader()
