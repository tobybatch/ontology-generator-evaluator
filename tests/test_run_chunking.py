from hashlib import sha256

import pytest

import config
from app import app
from ontology_generator_evaluator.models.run_model import RunModel
from ontology_generator_evaluator.models.run_status_model import RunStatusModel
from ontology_generator_evaluator.services import run_service


def _setup_run(monkeypatch, tmp_path, sources):
    monkeypatch.setattr(config, "STORAGE_PATH", str(tmp_path / "storage"))
    monkeypatch.setattr(config, "RUN_MODEL_STORAGE_PATH", str(tmp_path / "runs"))
    monkeypatch.setattr(config, "RUN_STATUS_MODEL_STORAGE_PATH", str(tmp_path / "statuses"))
    run = RunModel("run-chunks")
    run.processing_library = "Langchain"
    run.input_sources = [str(source) for source in sources]
    run.save()
    return run


def _chunk_dir(run, source):
    source_id = sha256(str(source).encode("utf-8")).hexdigest()
    return run_service.get_asset_storage_path(run.id) / "chunks" / source_id


def test_start_run_chunks_multiple_sources_and_resumes(monkeypatch, tmp_path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("first " * 1000, encoding="utf-8")
    second.write_text("second source", encoding="utf-8")
    run = _setup_run(monkeypatch, tmp_path, [first, second])

    data = run_service.start_run(run.id)

    assert data["run_model"] == run
    assert data["status"].source_processed == [str(first), str(second)]
    first_chunks = sorted(_chunk_dir(run, first).glob("chunk_*.txt"))
    assert len(first_chunks) > 1
    assert all(0 < len(chunk.read_text(encoding="utf-8")) <= 2500 for chunk in first_chunks)
    assert (_chunk_dir(run, second) / "chunk_000000.txt").read_text(encoding="utf-8") == "second source"
    assert RunStatusModel.load(f"{run.id}_status").source_processed == [str(first), str(second)]

    first.unlink()
    second.unlink()
    assert run_service.start_run(run.id)["status"].source_processed == [str(first), str(second)]


def test_failed_source_is_retried_without_reprocessing_completed_sources(monkeypatch, tmp_path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("completed", encoding="utf-8")
    second.write_bytes(b"\xff")
    run = _setup_run(monkeypatch, tmp_path, [first, second])

    with pytest.raises(UnicodeDecodeError):
        run_service.start_run(run.id)
    assert RunStatusModel.load(f"{run.id}_status").source_processed == [str(first)]

    first.unlink()
    second.write_text("retry", encoding="utf-8")
    chunk_dir = _chunk_dir(run, second)
    chunk_dir.mkdir(parents=True)
    (chunk_dir / "chunk_000001.txt").write_text("stale", encoding="utf-8")
    (chunk_dir / "notes.txt").write_text("keep", encoding="utf-8")
    status = run_service.start_run(run.id)["status"]

    assert status.source_processed == [str(first), str(second)]
    assert (chunk_dir / "chunk_000000.txt").read_text(encoding="utf-8") == "retry"
    assert not (chunk_dir / "chunk_000001.txt").exists()
    assert (chunk_dir / "notes.txt").read_text(encoding="utf-8") == "keep"


def test_start_route_does_not_execute_a_run(monkeypatch, tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("some text", encoding="utf-8")
    run = _setup_run(monkeypatch, tmp_path, [source])

    response = app.test_client().get("/start", query_string={"run_id": run.id})

    assert response.status_code == 200
    assert f"Run {run.name}" in response.get_data(as_text=True)
    assert not _chunk_dir(run, source).exists()


def test_empty_source_is_recorded_without_chunks(monkeypatch, tmp_path):
    source = tmp_path / "empty.txt"
    source.write_text("", encoding="utf-8")
    run = _setup_run(monkeypatch, tmp_path, [source])

    status = run_service.start_run(run.id)["status"]

    assert status.source_processed == [str(source)]
    assert list(_chunk_dir(run, source).glob("chunk_*.txt")) == []
