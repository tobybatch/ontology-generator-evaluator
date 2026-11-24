import os

import requests

from config import load_config

load_config()


class OpenAIProvider:
    @staticmethod
    def _headers() -> dict[str, str]:
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI.")
        return {"Authorization": f"Bearer {key}"}

    def get_models(self) -> list[dict]:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        models = response.json()["data"]
        model_ids = sorted({m["id"] for m in models if m["id"].startswith(("gpt-", "o1", "o3", "o4"))})

        return [
            {
                "name": model_id,
                "model": model_id,
            }
            for model_id in model_ids
        ]

    def generate(self, model: str, prompt: str) -> str:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=self._headers(),
            json={"model": model, "messages": [{"role": "user", "content": prompt}]},
            timeout=180,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise ValueError("OpenAI returned an empty generation response.")
        return content

    def embed(self, model: str, texts: list[str]) -> list[list[float]]:
        response = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers=self._headers(),
            json={"model": model, "input": texts},
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()["data"]
        ordered = sorted(data, key=lambda item: item["index"])
        if [item["index"] for item in ordered] != list(range(len(texts))):
            raise ValueError("OpenAI returned an incomplete embedding batch.")
        return [item["embedding"] for item in ordered]
