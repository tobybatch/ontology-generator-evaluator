import requests


def bytes_to_gb(size_bytes: int) -> str:
    return f"{size_bytes / 1024**3:.0f}GB"


class OllamaProvider:
    def get_models(self) -> list[dict]:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        response.raise_for_status()
        models = response.json()["models"]

        unique_models = {
            m["model"]: {
                "name": f"{m['name']} ({bytes_to_gb(m['size'])})",
                "model": m["model"],
            }
            for m in models
        }

        return [
            {
                "name": m["name"],
                "model": m["model"],
            }
            for m in unique_models.values()
        ]

    def generate(self, model: str, prompt: str) -> str:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=180,
        )
        response.raise_for_status()
        content = response.json()["response"]
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Ollama returned an empty generation response.")
        return content

    def embed(self, model: str, texts: list[str]) -> list[list[float]]:
        response = requests.post(
            "http://localhost:11434/api/embed",
            json={"model": model, "input": texts},
            timeout=180,
        )
        response.raise_for_status()
        return response.json()["embeddings"]
