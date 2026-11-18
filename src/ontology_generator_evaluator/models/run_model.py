from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import config

config.load_config()


def _get_run_file_path(run_id: str) -> Path:
    return _get_storage_path() / f"{run_id}.json"


def _get_storage_path() -> Path:
    storage_path = config.get_run_model_storage_path()
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


@dataclass
class RunModel:
    id: str
    name: str
    processing_library: str
    ai_provider: str
    ai_model: str
    input_sources: list[str] = field(default_factory=list)
    prompt: str = config.DEFAULT_PROMPT

    def __init__(self, run_id: str) -> None:
        self.id = run_id
        self.name = run_id
        self.processing_library = ""
        self.ai_provider = ""
        self.ai_model = ""
        self.input_sources = []
        self.prompt = config.DEFAULT_PROMPT

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save(self) -> None:
        with _get_run_file_path(self.id).open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    def update(self) -> None:
        self.delete()
        self.save()

    def delete(self) -> None:
        _get_run_file_path(self.id).unlink(missing_ok=True)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> RunModel:
        obj = cls(data.get("id", ""))
        obj.name = data["name"]
        obj.processing_library = data["processing_library"]
        obj.ai_provider = data["ai_provider"]
        obj.ai_model = data["ai_model"]
        obj.input_sources = list(data.get("input_sources", []))
        obj.prompt = data.get("prompt", config.DEFAULT_PROMPT)
        return obj

    @classmethod
    def from_request(cls, request_form: Mapping[str, str]) -> RunModel:
        run_id = request_form.get("run_id") or f"run.{datetime.now():%Y-%m-%d.%H-%M-%S}"
        files_path = Path(config.STORAGE_PATH) / run_id
        input_sources = [str(file) for file in files_path.iterdir() if file.is_file()] if files_path.is_dir() else []

        obj = cls(run_id=run_id)
        obj.name = request_form.get("run_name", "")
        obj.processing_library = request_form.get("processing_library", "")
        obj.ai_provider = request_form.get("ai_provider", "")
        obj.ai_model = request_form.get("ai_model", "")
        obj.input_sources = input_sources
        obj.prompt = request_form.get("processing_prompt", config.DEFAULT_PROMPT)
        return obj

    @staticmethod
    def load(run_id: str) -> RunModel:
        file_path = _get_run_file_path(run_id)
        with file_path.open(encoding="utf-8") as f:
            data = json.load(f)
        return RunModel.from_dict(data)

    @staticmethod
    def list() -> list[Path]:
        storage_path = _get_storage_path()
        return sorted(file for file in storage_path.glob("*.json") if file.is_file())

