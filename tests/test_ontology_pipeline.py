import json

import pytest
from rdflib import Graph, URIRef

import config
from ontology_generator_evaluator.services import job_queue, ontology_pipeline, worker


class Provider:
    def __init__(self):
        self.prompts = []
        self.fail = False

    def embed(self, model, texts):
        assert model == "embedding"
        return [[float(i + 1), 1.0] for i in range(len(texts))]

    def generate(self, model, prompt):
        assert model == "chat"
        self.prompts.append(prompt)
        if self.fail:
            return "invalid turtle ["
        return '@prefix ex: <https://example.org/> . ex:Cat ex:label "cat"@en; ex:type ex:Animal .'


def _snapshot(texts):
    return {
        "run": {
            "processing_library": "Langchain",
            "ai_provider": "fake",
            "ai_model": "chat",
            "embedding_model": "embedding",
            "base_iri": "https://example.org/",
            "prompt": "Find concepts",
        },
        "sources": [{"path": f"source-{i}.txt", "text": text} for i, text in enumerate(texts)],
    }


def test_pipeline_covers_all_chunks_and_preserves_rdf(monkeypatch, tmp_path):
    provider = Provider()
    monkeypatch.setitem(ontology_pipeline.AI_PROVIDERS, "fake", provider)
    stages = []
    ontology_pipeline.build_ontology(_snapshot(["first", "second", "third"]), tmp_path, stages.append)
    assert len(provider.prompts) == 3
    for text, prompt in zip(["first", "second", "third"], provider.prompts, strict=True):
        assert f"ANCHOR TEXT:\n{text}" in prompt
        assert "RELATED CONTEXT:" in prompt
    graph = Graph().parse(tmp_path / "ontology.ttl", format="turtle")
    assert len(graph) == 2
    data = json.loads((tmp_path / "graph.json").read_text())
    assert data["version"] == 1
    assert len(data["edges"]) == 1
    attributes = [attribute for node in data["nodes"] for attribute in node["attributes"]]
    assert attributes[0]["value"] == {"type": "literal", "value": "cat", "language": "en"}
    assert (
        URIRef("https://example.org/Cat"),
        URIRef("https://example.org/type"),
        URIRef("https://example.org/Animal"),
    ) in graph
    assert len(json.loads((tmp_path / "vectors.json").read_text())["chunks"]) == 3


def test_invalid_embedding_or_turtle_fails(monkeypatch, tmp_path):
    provider = Provider()
    monkeypatch.setitem(ontology_pipeline.AI_PROVIDERS, "fake", provider)
    provider.fail = True
    with pytest.raises(ValueError, match="Invalid Turtle.*source-0.txt"):
        ontology_pipeline.build_ontology(_snapshot(["first"]), tmp_path, lambda _: None)
    assert not (tmp_path / "ontology.ttl").exists()
    monkeypatch.setattr(provider, "embed", lambda model, texts: [[0, 0]])
    with pytest.raises(ValueError, match="zero"):
        ontology_pipeline.build_ontology(_snapshot(["first"]), tmp_path, lambda _: None)


def test_queue_claim_recovery_and_fencing(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "STORAGE_PATH", str(tmp_path))
    job_id = job_queue.enqueue("run", _snapshot(["text"]))
    with pytest.raises(ValueError, match="already"):
        job_queue.enqueue("run", _snapshot(["text"]))
    first = job_queue.claim()
    assert first["id"] == job_id
    assert job_queue.claim() is None
    with job_queue._connect() as db:
        db.execute("UPDATE jobs SET lease_until = 0 WHERE id = ?", (job_id,))
    second = job_queue.claim()
    assert second["token"] != first["token"]
    assert not job_queue.finish(job_id, first["token"], result_dir="stale")
    assert job_queue.finish(job_id, second["token"], error="failure")
    assert job_queue.latest("run")["error"] == "failure"
    assert job_queue.enqueue("run", _snapshot(["text"])) != job_id


def test_worker_failure_is_visible_and_retryable(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "STORAGE_PATH", str(tmp_path))
    provider = Provider()
    provider.fail = True
    monkeypatch.setitem(ontology_pipeline.AI_PROVIDERS, "fake", provider)
    job_queue.enqueue("run", _snapshot(["text"]))
    assert worker.run_one()
    failed = job_queue.latest("run")
    assert failed["state"] == "failed"
    assert "Invalid Turtle" in failed["error"]
    assert failed["result_dir"] is None
    provider.fail = False
    job_queue.enqueue("run", _snapshot(["text"]))
    assert worker.run_one()
    assert job_queue.latest("run")["state"] == "completed"


def test_graph_json_preserves_blank_nodes_and_typed_literals():
    graph = Graph().parse(
        data="@prefix ex: <https://example.org/> . ex:a ex:relation [ ex:count 3 ] .",
        format="turtle",
    )
    result = ontology_pipeline.graph_json(graph)
    blank = next(node for node in result["nodes"] if node["id"]["type"] == "blank")
    assert blank["attributes"][0]["value"] == {
        "type": "literal",
        "value": "3",
        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
    }
    assert result["edges"][0]["target"] == blank["id"]
    assert ontology_pipeline.graph_json(graph) == result
