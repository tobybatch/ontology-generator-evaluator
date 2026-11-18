import json

import config
from ontology_generator_evaluator.models.run_model import RunModel


def test_from_request_reads_form_fields_and_uploaded_document_paths(tmp_path, monkeypatch):
    storage_path = tmp_path / "storage"
    documents_path = storage_path / "run-1"
    documents_path.mkdir(parents=True)
    document = documents_path / "source.pdf"
    document.touch()
    (documents_path / "nested").mkdir()
    monkeypatch.setattr(config, "STORAGE_PATH", str(storage_path))

    run_model = RunModel.from_request(
        {
            "run_id": "run-1",
            "run_name": "A test run",
            "processing_library": "Langchain",
            "ai_provider": "OpenAI",
            "ai_model": "gpt-test",
            "processing_prompt": "Extract entities",
        }
    )

    assert run_model.id == "run-1"
    assert run_model.name == "A test run"
    assert run_model.processing_library == "Langchain"
    assert run_model.ai_provider == "OpenAI"
    assert run_model.ai_model == "gpt-test"
    assert run_model.input_sources == [str(document)]
    assert run_model.prompt == "Extract entities"


def test_from_request_uses_defaults_when_form_fields_are_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "STORAGE_PATH", str(tmp_path / "storage"))

    run_model = RunModel.from_request({})

    assert run_model.id.startswith("run.")
    assert run_model.name == ""
    assert run_model.processing_library == ""
    assert run_model.ai_provider == ""
    assert run_model.ai_model == ""
    assert run_model.input_sources == []
    assert run_model.prompt == ""


def test_save_load_list_update_and_delete(tmp_path, monkeypatch):
    storage_path = tmp_path / "runs"
    monkeypatch.setattr(config, "RUN_MODEL_STORAGE_PATH", str(storage_path))
    run_model = RunModel(
        id="run-1",
        name="First run",
        processing_library="Langchain",
        ai_provider="OpenAI",
        ai_model="gpt-test",
        input_sources=["source.pdf"],
        prompt="Extract entities",
    )

    run_model.save()

    saved_data = json.loads((storage_path / "run-1.json").read_text(encoding="utf-8"))
    assert saved_data == run_model.to_dict()
    assert RunModel.load("run-1") == run_model
    assert RunModel.list() == [storage_path / "run-1.json"]

    run_model.name = "Updated run"
    run_model.update()
    assert RunModel.load("run-1").name == "Updated run"

    run_model.delete()
    assert not (storage_path / "run-1.json").exists()
    assert RunModel.list() == []


def test_from_dict_supports_legacy_optional_fields():
    run_model = RunModel.from_dict(
        {
            "name": "Legacy run",
            "processing_library": "Langchain",
            "ai_provider": "OpenAI",
            "ai_model": "gpt-test",
        }
    )

    assert run_model.id == ""
    assert run_model.input_sources == []
    assert run_model.prompt == ""
