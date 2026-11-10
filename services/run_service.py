import os

import requests

from config import load_config

load_config()


def get_dashboard_data():
    raw_models = _get_ollama_models() + _get_openai_models()

    # Sort models by their full provider:model identifier
    formatted_models = [
        {
            "text": m["model"],
            "value": m["model"],
        }
        for m in sorted(raw_models, key=lambda m: m["model"])
    ]

    return {"models": formatted_models}


def _get_ollama_models():
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
            "model": f"ollama:{m['model']}",
        }
        for m in unique_models.values()
    ]


def _get_openai_models():
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
            "model": f"openai:{model_id}",
        }
        for model_id in model_ids
    ]
