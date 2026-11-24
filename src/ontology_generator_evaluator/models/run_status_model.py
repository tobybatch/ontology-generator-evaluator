from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import config

config.load_config()


def _get_run_status_file_path(run_status_id):
    return _get_storage_path() / f"{run_status_id}.json"


def _get_storage_path() -> Path:
    storage_path = config.get_run_status_model_storage_path()
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


@dataclass
class RunStatusModel:
    id: str
    run_model_id: str
    source_processed: list[str] = field(default_factory=list)

    def __init__(self, run_model_id: str) -> None:
        self.id = run_model_id + "_status"
        self.run_model_id = run_model_id
        self.source_processed = []

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save(self) -> None:
        with _get_run_status_file_path(self.id).open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> RunStatusModel:
        obj = cls(data.get("run_model_id", ""))
        obj.id = data.get("id", obj.run_model_id + "_status")
        obj.run_model_id = data.get("run_model_id", "")
        obj.source_processed = list(data.get("source_processed", []))
        return obj

    @staticmethod
    def load(run_status_id: str) -> RunStatusModel:
        file_path = _get_run_status_file_path(run_status_id)
        with file_path.open(encoding="utf-8") as f:
            data = json.load(f)
        return RunStatusModel.from_dict(data)

    @staticmethod
    def load_or_create(run_model_id: str) -> RunStatusModel:
        run_status_id = run_model_id + "_status"
        file_path = _get_run_status_file_path(run_status_id)
        if file_path.exists():
            return RunStatusModel.load(run_status_id)
        else:
            return RunStatusModel(run_model_id)
