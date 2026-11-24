import config
from ontology_generator_evaluator.models.run_status_model import RunStatusModel


def test_init_sets_run_id_and_empty_status():
    model = RunStatusModel("run-1")
    assert model.id == "run-1_status"
    assert model.run_model_id == "run-1"
    assert model.source_processed == []


def test_from_dict_and_to_dict_round_trip():
    data = {"id": "run-1_status", "run_model_id": "run-1", "source_processed": ["source.txt"]}
    assert RunStatusModel.from_dict(data).to_dict() == data


def test_load_or_create_uses_status_identifier(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "RUN_STATUS_MODEL_STORAGE_PATH", str(tmp_path))
    status = RunStatusModel.load_or_create("run-1")
    status.source_processed.append("source.txt")
    status.save()
    assert RunStatusModel.load_or_create("run-1") == status
