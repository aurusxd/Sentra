from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from backend.config import OPENROUTER_API_KEY

from backend.database.models.knowledge_file import KnowledgeFile
from backend.utils.logger import log


class VectorStoreService:
    embeddings = OpenAIEmbeddings(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        model="nvidia/llama-nemotron-embed-vl-1b-v2:free",
    )

    async def find_vectors(
        self, collection_name: str, question: str, chunk_size: int
    ) -> list[KnowledgeFile]:
        """
        Ищет похожие вектор исходя из заданного вопроса

        Возвращает: список чанков

        """
        vector_store = Chroma(
            collection_name=collection_name,
            persist_directory="backend/database/chroma/chroma_db",
            embedding_function=self.embeddings,
        )
        try:
            return vector_store.similarity_search(
                question,
                k=chunk_size,
            )
        except Exception as e:
            log.exception("Ошибка поиска векторов: ", e)
            raise


vector_store_service = VectorStoreService()
