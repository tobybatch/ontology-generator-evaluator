from ontology_generator_evaluator.models.run_status_model import RunStatusModel


def test_init_sets_run_id_and_empty_status():
    model = RunStatusModel("run-1")

    assert model.id == "run-1"
    assert model.run_id == "run-1"
    assert model.input_sources == []
    assert model.source_in_progress == ""
    assert model.source_processed == []


def test_from_dict_and_to_dict_round_trip():
    data = {
        "id": "status-1",
        "run_id": "run-1",
        "input_sources": ["source-1.pdf", "source-2.pdf"],
        "source_in_progress": "source-2.pdf",
        "source_processed": ["source-1.pdf"],
    }

    model = RunStatusModel.from_dict(data)

    assert model.to_dict() == data


def test_from_dict_defaults_missing_status_fields():
    model = RunStatusModel.from_dict({"run_id": "run-1"})

    assert model.to_dict() == {
        "id": "run-1",
        "run_id": "run-1",
        "input_sources": [],
        "source_in_progress": "",
        "source_processed": [],
    }
