import json
from pathlib import Path

import config
from ontology_generator_evaluator.models.run_model import RunModel

config.load_config()


def _get_storage_path() -> Path:
    storage_path = config.get_run_model_storage_path()
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


def _get_run_file_path(run_id: str) -> Path:
    return _get_storage_path() / f"{run_id}.json"


def save_run_model(obj: RunModel) -> None:
    file_path = _get_run_file_path(obj.id)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(obj.to_dict(), f, indent=2)


def load_run_model(run_id: str) -> RunModel:
    file_path = _get_run_file_path(run_id)
    with file_path.open(encoding="utf-8") as f:
        data = json.load(f)
    return RunModel.from_dict(data)


def list_runs() -> list[Path]:
    storage_path = _get_storage_path()
    return sorted(file for file in storage_path.glob("*.json") if file.is_file())


def delete_run(run_id: str) -> None:
    _get_run_file_path(run_id).unlink(missing_ok=True)