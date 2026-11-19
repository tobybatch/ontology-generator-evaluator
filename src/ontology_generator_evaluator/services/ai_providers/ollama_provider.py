import requests


def bytes_to_gb(size_bytes: int) -> str:
    return f"{size_bytes / 1024**3:.0f}GB"


class OllamaProvider:

    def get_models(self) -> list[dict]:
        models = requests.get("http://localhost:11434/api/tags").json()["models"]

        for model in models:
            print(model)

        unique_models = {
            m["model"]: {
                "name": f'{m["name"]} ({bytes_to_gb(m["size"])})',
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
