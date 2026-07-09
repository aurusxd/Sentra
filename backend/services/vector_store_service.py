from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from backend.config import OPENROUTER_API_KEY

from backend.database.models.knowledge_file import KnowledgeFile
from backend.utils.logger import log
from langchain_huggingface import HuggingFaceEmbeddings

class VectorStoreService:
    embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    async def find_vectors(
        self,
        employee_id: int,
        question: str,
        k: int = 5,
    ) -> list[KnowledgeFile]:
        """
        Ищет похожие вектор исходя из заданного вопроса

        Возвращает: список чанков

        """
        vector_store = Chroma(
            collection_name=f"employee_{employee_id}",
            persist_directory="backend/database/chroma/chroma_db",
            embedding_function=self.embeddings,
        )
        try:
            return vector_store.similarity_search(
            question,
            k=k,
            )
        except Exception as e:
            log.exception("Ошибка поиска векторов")
            raise


vector_store_service = VectorStoreService()
