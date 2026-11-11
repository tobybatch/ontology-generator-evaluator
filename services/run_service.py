from flask import jsonify

from config import load_config
from services.providers.ollama_provider import OllamaProvider
from services.providers.openapi_provider import OpenAIProvider

load_config()

AI_PROVIDERS = {
    "OpenAI": OpenAIProvider(),
    "Ollama": OllamaProvider(),
}

def get_dashboard_data():
    # raw_models = _get_ollama_models() + _get_openai_models()
    # Sort models by their full provider:model identifier
    # formatted_models = [
    #     {
    #         "text": m["model"],
    #         "value": m["model"],
    #     }
    #     for m in sorted(raw_models, key=lambda m: m["model"])
    # ]

    return {"ai_providers": [{"text": key, "value": key} for key in AI_PROVIDERS.keys()]}
