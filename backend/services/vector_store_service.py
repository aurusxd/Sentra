from langchain_chroma import Chroma
from langchain_core.documents import Document

from backend.services.openrouter_embeddings import openrouter_embeddings
from backend.utils.logger import log


class VectorStoreService:
    async def find_vectors(
        self,
        employee_id: int,
        question: str,
        k: int = 5,
    ) -> list[Document]:
        """
        Ищет релевантные чанки во всех документах сотрудника.
        """

        vector_store = Chroma(
            collection_name=f"employee_{employee_id}",
            persist_directory="backend/database/chroma/chroma_db",
            embedding_function=openrouter_embeddings,
        )

        try:
            documents = vector_store.similarity_search(
                query=question,
                k=k,
            )

            log.info(
                f"Found {len(documents)} chunks "
                f"for employee_{employee_id}"
            )

            return documents

        except Exception:
            log.exception(
                f"Failed vector search for employee_{employee_id}"
            )
            raise


vector_store_service = VectorStoreService()