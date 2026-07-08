from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from backend.database.models.knowledge_file import KnowledgeFile
from backend.utils.logger import log
from backend.config import OPENROUTER_API_KEY


class EmbeddingService:
    embeddings = OpenAIEmbeddings(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        model="nvidia/llama-nemotron-embed-vl-1b-v2:free",
    )

    async def generate_embedding(
        self, chunks: list[KnowledgeFile], document_name: str
    ) -> bool:
        """
        Генерирует вектора с последующим их сохранением в chromaDB
        Возвращает: true-успешно, false-неуспешно
        """
        try:
            Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory="backend/database/chroma/chroma_db",
                collection_name=document_name,
            )
            return True
        except Exception as e:
            log.exception("Ошибка создания векторов: ", e)
            return False

embedding_service = EmbeddingService()