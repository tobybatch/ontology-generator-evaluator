from unittest.mock import Mock

import pytest

from ontology_generator_evaluator.services.ai_providers.ollama_provider import OllamaProvider
from ontology_generator_evaluator.services.ai_providers.openapi_provider import OpenAIProvider


def test_openai_models_are_passed_and_embedding_order_is_checked(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    post = Mock()
    post.return_value.json.side_effect = [
        {"data": [{"index": 1, "embedding": [2]}, {"index": 0, "embedding": [1]}]},
        {"choices": [{"message": {"content": "turtle"}}]},
        {"data": [{"index": 1, "embedding": [2]}]},
    ]
    monkeypatch.setattr("ontology_generator_evaluator.services.ai_providers.openapi_provider.requests.post", post)
    provider = OpenAIProvider()
    assert provider.embed("embed-model", ["a", "b"]) == [[1], [2]]
    assert post.call_args.kwargs["json"]["model"] == "embed-model"
    assert provider.generate("chat-model", "prompt") == "turtle"
    assert post.call_args.kwargs["json"]["model"] == "chat-model"
    with pytest.raises(ValueError, match="incomplete"):
        provider.embed("embed-model", ["a"])


def test_ollama_embeds_and_generates_without_streaming(monkeypatch):
    post = Mock()
    post.return_value.json.side_effect = [{"embeddings": [[1, 2]]}, {"response": "turtle"}]
    monkeypatch.setattr("ontology_generator_evaluator.services.ai_providers.ollama_provider.requests.post", post)
    provider = OllamaProvider()
    assert provider.embed("embed-model", ["a"]) == [[1, 2]]
    assert provider.generate("chat-model", "prompt") == "turtle"
    assert post.call_args.kwargs["json"]["stream"] is False
