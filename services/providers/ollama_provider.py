import requests


class OllamaProvider:

    def get_models(self) -> list[dict]:
        models = requests.get("http://localhost:11434/api/tags").json()["models"]

        unique_models = {
            m["model"]: {
                "name": m["name"],
                "model": m["model"],
            }
            for m in models
        }

        return [
            {
                "name": m["name"],
                "model": m['model'],
            }
            for m in unique_models.values()
        ]

    def generate(self, prompt: str) -> str:
        ...
