from ontology_generator_evaluator.services.ai_providers.ollama_provider import OllamaProvider
from ontology_generator_evaluator.services.ai_providers.openapi_provider import OpenAIProvider

AI_PROVIDERS = {
    "OpenAI": OpenAIProvider(),
    "Ollama": OllamaProvider(),
}

EMBEDDING_MODELS = {
    "OpenAI": ["text-embedding-3-small", "text-embedding-3-large"],
    "Ollama": ["nomic-embed-text"],
}
