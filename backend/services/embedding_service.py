from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from backend.config import OPENROUTER_API_KEY


class EmbeddingService:
    embeddings = OpenAIEmbeddings(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        model="nvidia/llama-nemotron-embed-vl-1b-v2:free",
    )

    async def add_chunks(
        self,
        employee_id: int,
        knowledge_file_id: int,
        document_name: str,
        chunks: list[str],
    ) -> bool:
        documents = [
            Document(
                page_content=chunk,
                metadata={
                    "employee_id": employee_id,
                    "knowledge_file_id": knowledge_file_id,
                    "document_name": document_name,
                    "chunk_index": index,
                },
            )
            for index, chunk in enumerate(chunks)
        ]

        vector_store = Chroma(
            collection_name=f"employee_{employee_id}",
            persist_directory="backend/database/chroma/chroma_db",
            embedding_function=self.embeddings,
        )

        vector_store.add_documents(documents)

        return True