from langchain_chroma import Chroma
from langchain_core.documents import Document

from backend.services.openrouter_embeddings import openrouter_embeddings
from backend.utils.logger import log


class EmbeddingService:
    async def add_chunks(
        self,
        employee_id: int,
        knowledge_file_id: int,
        document_name: str,
        chunks: list[Document],
    ) -> bool:
        """
        Генерирует embeddings чанков и сохраняет их в Chroma.
        """

        try:
            documents: list[Document] = []

            for index, chunk in enumerate(chunks):
                documents.append(
                    Document(
                        page_content=chunk.page_content,
                        metadata={
                            "employee_id": employee_id,
                            "knowledge_file_id": knowledge_file_id,
                            "document_name": document_name,
                            "chunk_index": index,
                        },
                    )
                )

            vector_store = Chroma(
                collection_name=f"employee_{employee_id}",
                persist_directory="backend/database/chroma/chroma_db",
                embedding_function=openrouter_embeddings,
            )

            vector_store.add_documents(documents)

            log.success(
                f"Added {len(documents)} chunks "
                f"to employee_{employee_id}"
            )

            return True

        except Exception:
            log.exception(
                f"Failed to create embeddings for {document_name}"
            )
            return False


embedding_service = EmbeddingService()