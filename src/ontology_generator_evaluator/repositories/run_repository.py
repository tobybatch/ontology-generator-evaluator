import json
from pathlib import Path

from ontology_generator_evaluator.models.run_model import RunModel


class RunModelRepository:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path

    def save(self, obj: RunModel) -> None:
        with open(self.storage_path, "w") as f:
            json.dump(obj.to_dict(), f, indent=2)

    def load(self) -> RunModel:
        with open(self.storage_path) as f:
            data = json.load(f)

        return RunModel.from_dict(data)