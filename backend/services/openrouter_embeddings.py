from openai import OpenAI
from langchain_core.embeddings import Embeddings

from backend.config import OPENROUTER_API_KEY
from backend.utils.logger import log


class OpenRouterEmbeddings(Embeddings):
    def __init__(self) -> None:
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
            timeout=30.0,
        )

        self.model = "nvidia/llama-nemotron-embed-vl-1b-v2:free"

    def _embed_text(self, text: str) -> list[float]:
        """
        Создает embedding одного текста.
        """

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=[
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": text,
                            }
                        ]
                    }
                ],
                encoding_format="float",
                extra_headers={
                    "HTTP-Referer": "https://sentra.fun",
                    "X-OpenRouter-Title": "Sentra",
                },
            )

            if not response.data:
                raise ValueError("OpenRouter returned empty embedding data")

            return response.data[0].embedding

        except Exception:
            log.exception("Failed to create OpenRouter embedding")
            raise

    def embed_query(self, text: str) -> list[float]:
        """
        Создает embedding поискового запроса пользователя.
        """

        return self._embed_text(text)

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Создает embeddings для списка чанков документов.
        """

        return [
            self._embed_text(text)
            for text in texts
        ]


openrouter_embeddings = OpenRouterEmbeddings()