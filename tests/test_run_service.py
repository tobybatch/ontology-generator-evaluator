from io import BytesIO

from werkzeug.test import create_environ
from werkzeug.wrappers import Request

import config
from ontology_generator_evaluator.models.run_model import RunModel
from ontology_generator_evaluator.services import run_service


def _request(method="GET", *, query_string=None, data=None):
    return Request(
        create_environ(
            "/",
            method=method,
            query_string=query_string,
            data=data,
        )
    )


def _set_storage_paths(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "STORAGE_PATH", str(tmp_path / "storage"))
    monkeypatch.setattr(config, "RUN_MODEL_STORAGE_PATH", str(tmp_path / "runs"))


def test_get_dashboard_data_creates_new_run_data(monkeypatch, tmp_path):
    _set_storage_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(run_service, "_generate_timestamped_name", lambda prefix: f"{prefix}.fixed")

    data = run_service.get_dashboard_data(_request())

    assert data["run_model"] == RunModel("run.fixed")
    assert data["previous_runs"] == []
    assert data["input_source_checkbox_values"] == []
    assert [item["value"] for item in data["lib_providers"]] == list(run_service.LIB_PROVIDERS)
    assert [item["value"] for item in data["ai_providers"]] == list(run_service.AI_PROVIDERS)
    assert data["errors"] == {}


def test_get_dashboard_data_loads_requested_run_and_lists_saved_runs(monkeypatch, tmp_path):
    _set_storage_paths(monkeypatch, tmp_path)
    saved_run = RunModel("run-saved")
    saved_run.name = "Saved run"
    saved_run.processing_library = "Langchain"
    saved_run.ai_provider = "OpenAI"
    saved_run.ai_model = "gpt-test"
    saved_run.input_sources = ["source.pdf"]
    saved_run.prompt = "Extract entities"
    saved_run.save()

    data = run_service.get_dashboard_data(_request(query_string="run=run-saved"))

    assert data["run_model"] == saved_run
    assert data["previous_runs"] == [{"value": "run-saved", "text": "run-saved"}]
    assert data["input_source_checkbox_values"] == [{"value": "source.pdf", "text": "source.pdf"}]


def test_post_saves_run_and_sanitizes_uploaded_document_name(monkeypatch, tmp_path):
    _set_storage_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(run_service, "_generate_timestamped_name", lambda prefix: f"{prefix}.fixed")
    request = _request(
        method="POST",
        data={
            "run_id": "run-upload",
            "run_name": "",
            "processing_library": "Langchain",
            "ai_provider": "OpenAI",
            "ai_model": "gpt-test",
            "processing_prompt": "Extract entities",
            "input_docs": (BytesIO(b"document contents"), "../../source document.pdf"),
        },
    )

    data = run_service.get_dashboard_data(request)

    document = tmp_path / "storage" / "run-upload" / "source_document.pdf"
    assert document.read_bytes() == b"document contents"
    assert data["run_model"].name == "run.fixed"
    assert data["run_model"].input_sources == [str(document)]
    assert RunModel.load("run-upload") == data["run_model"]
    assert data["previous_runs"] == [{"value": "run-upload", "text": "run-upload"}]
    assert data["input_source_checkbox_values"] == [{"value": str(document), "text": str(document)}]


def test_post_without_upload_saves_run(monkeypatch, tmp_path):
    _set_storage_paths(monkeypatch, tmp_path)
    request = _request(
        method="POST",
        data={
            "run_id": "run-no-upload",
            "run_name": "No upload",
            "processing_library": "Langchain",
            "ai_provider": "Ollama",
            "ai_model": "llama-test",
            "processing_prompt": "Extract entities",
        },
    )

    data = run_service.get_dashboard_data(request)

    assert data["run_model"].name == "No upload"
    assert data["run_model"].input_sources == []
    assert RunModel.load("run-no-upload") == data["run_model"]
