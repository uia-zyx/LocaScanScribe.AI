import httpx

from app.core.settings import get_settings


class EmbeddingClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def embed(self, text: str) -> list[float]:
        payload = {
            "model": self.settings.llama_embedding_model,
            "input": text,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.settings.llama_embedding_base_url}/embeddings",
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        embedding = data["data"][0]["embedding"]
        return [float(value) for value in embedding]
