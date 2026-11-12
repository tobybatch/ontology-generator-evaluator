import os
import requests


from config import load_config

load_config()


class OpenAIProvider:

    def get_models(self) -> list[dict]:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
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

    def generate(self, prompt: str) -> str:
        ...
