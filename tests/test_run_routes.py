from io import BytesIO

import config
from app import app
from ontology_generator_evaluator.models.run_model import RunModel
from ontology_generator_evaluator.services import job_queue, worker


class FakeProvider:
    def embed(self, model, texts):
        return [[1.0, float(i + 1)] for i in range(len(texts))]

    def generate(self, model, prompt):
        return "@prefix ex: <https://example.org/ontology/> . ex:Cat a ex:Animal ."


def _setup(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "STORAGE_PATH", str(tmp_path / "storage"))
    monkeypatch.setattr(config, "RUN_MODEL_STORAGE_PATH", str(tmp_path / "runs"))
    monkeypatch.setitem(worker.build_ontology.__globals__["AI_PROVIDERS"], "OpenAI", FakeProvider())


def test_start_saves_form_queues_worker_and_downloads(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)
    client = app.test_client()
    response = client.post(
        "/",
        data={
            "action": "start",
            "run_id": "run-actions",
            "run_name": "Saved changes",
            "processing_library": "Langchain",
            "ai_provider": "OpenAI",
            "ai_model": "chat",
            "embedding_model": "embed",
            "base_iri": "https://example.org/ontology/",
            "processing_prompt": "Find concepts",
            "input_docs": (BytesIO(b"Cat is an animal."), "input.txt"),
        },
    )
    assert response.status_code == 302
    assert RunModel.load("run-actions").embedding_model == "embed"
    assert job_queue.latest("run-actions")["state"] == "queued"
    assert client.get("/download/run-actions/ontology.ttl").status_code == 404
    assert worker.run_one()
    assert job_queue.latest("run-actions")["state"] == "completed"
    assert b"Download Turtle" in client.get(response.location).data
    assert client.get("/download/run-actions/ontology.ttl").status_code == 200
    assert client.get("/download/run-actions/graph.json").json["version"] == 1
    assert client.get("/download/run-actions/vectors.json").status_code == 404
    source = tmp_path / "storage" / "run-actions" / "input.txt"
    source.write_text("changed", encoding="utf-8")
    assert client.get("/download/run-actions/ontology.ttl").status_code == 404
    assert b"input has changed" in client.get(response.location).data


def test_invalid_start_is_saved_and_reports_error(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)
    response = app.test_client().post(
        "/",
        data={
            "action": "start",
            "run_id": "invalid",
            "run_name": "Saved changes",
        },
    )
    assert response.status_code == 400
    assert b"Select a valid processing library" in response.data
    assert RunModel.load("invalid").name == "Saved changes"
    assert job_queue.latest("invalid") is None


def test_update_saves_without_enqueue(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)
    response = app.test_client().post(
        "/",
        data={
            "action": "update",
            "run_id": "update",
            "run_name": "Updated",
        },
    )
    assert response.status_code == 200
    assert RunModel.load("update").name == "Updated"
    assert job_queue.latest("update") is None


def test_removed_sources_stay_removed_and_uploads_preserve_other_sources(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)
    client = app.test_client()
    common = {"action": "update", "run_id": "documents", "run_name": "Documents"}
    client.post("/", data={**common, "input_docs": (BytesIO(b"first"), "first.txt")})
    client.post("/", data={**common, "input_docs": (BytesIO(b"second"), "second.txt")})
    sources = RunModel.load("documents").input_sources
    assert len(sources) == 2
    client.post("/", data={**common, "documents": sources[0]})
    assert RunModel.load("documents").input_sources == [sources[1]]
    client.post("/", data=common)
    assert RunModel.load("documents").input_sources == [sources[1]]


def test_invalid_run_id_rejected(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)
    response = app.test_client().post("/", data={"action": "update", "run_id": "../outside"})
    assert response.status_code == 400


def test_embedding_models_are_specific_to_provider():
    client = app.test_client()
    assert client.get("/update_embedding_models?ai_provider=OpenAI").json == [
        "text-embedding-3-small",
        "text-embedding-3-large",
    ]
    assert client.get("/update_embedding_models?ai_provider=Ollama").json == ["nomic-embed-text"]
