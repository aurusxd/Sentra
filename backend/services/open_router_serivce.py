import requests
from typing import List
from langchain_core.embeddings import Embeddings
import asyncio

class OpenRouterEmbeddings(Embeddings):
    """Обертка для OpenRouter API, совместимая с LangChain"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "nvidia/llama-nemotron-embed-vl-1b-v2:free",
        site_url: str = "",
        site_name: str = ""
    ):
        self.api_key = api_key
        self.model = model
        self.site_url = site_url
        self.site_name = site_name
        self.base_url = "https://openrouter.ai/api/v1/embeddings"
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Генерирует эмбеддинги для списка текстов (синхронно)"""
        results = []
        for text in texts:
            embedding = self._get_embedding(text)
            results.append(embedding)
        return results
    
    def embed_query(self, text: str) -> List[float]:
        """Генерирует эмбеддинг для одного запроса"""
        return self._get_embedding(text)
    
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Асинхронная версия для массовой генерации"""
        tasks = [self._aget_embedding(text) for text in texts]
        return await asyncio.gather(*tasks)
    
    async def aembed_query(self, text: str) -> List[float]:
        """Асинхронная версия для одного запроса"""
        return await self._aget_embedding(text)
    
    def _get_embedding(self, text: str) -> List[float]:
        """Синхронный запрос к OpenRouter"""
        response = requests.post(
            url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.site_url,
                "X-OpenRouter-Title": self.site_name,
            },
            json={
                "model": self.model,
                "input": text,  # можно передать строку или список
                "encoding_format": "float"
            }
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
    
    async def _aget_embedding(self, text: str) -> List[float]:
        """Асинхронный запрос к OpenRouter"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": self.site_url,
                    "X-OpenRouter-Title": self.site_name,
                },
                json={
                    "model": self.model,
                    "input": text,
                    "encoding_format": "float"
                }
            ) as response:
                data = await response.json()
                return data["data"][0]["embedding"]