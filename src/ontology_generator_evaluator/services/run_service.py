from config import load_config
from ontology_generator_evaluator.services.ai_providers import AI_PROVIDERS
from ontology_generator_evaluator.services.lib_providers import LIB_PROVIDERS

load_config()


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

    return {
        "lib_providers": [{"text": key, "value": key} for key in LIB_PROVIDERS.keys()],
        "ai_providers": [{"text": key, "value": key} for key in AI_PROVIDERS.keys()],
        "processing_prompt": "default prompt text",
        "input_documents": []
    }
