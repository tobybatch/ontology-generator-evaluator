import json
from pathlib import Path

import config
from config import load_config
from ontology_generator_evaluator.models.run_model import RunModel

load_config()


def _get_storage_path() -> Path:
    storage_path = config.get_run_model_storage_path()
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


def save_run_model(obj: RunModel) -> None:
    file_path = _get_storage_path() / f"{obj.id}.json"
    with open(file_path, "w") as f:
        json.dump(obj.to_dict(), f, indent=2)


def load_run_model(run_id: str) -> RunModel:
    file_path = _get_storage_path() / f"{run_id}.json"
    with open(file_path) as f:
        data = json.load(f)

    return RunModel.from_dict(data)
