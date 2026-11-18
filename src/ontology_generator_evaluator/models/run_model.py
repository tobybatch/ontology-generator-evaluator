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
        return cls(
            id=data.get("id", ""),
            name=data["name"],
            processing_library=data["processing_library"],
            ai_provider=data["ai_provider"],
            ai_model=data["ai_model"],
            input_sources=list(data.get("input_sources", [])),
            prompt=data.get("prompt", config.DEFAULT_PROMPT),
        )

    @classmethod
    def from_request(cls, request_form: Mapping[str, str]) -> RunModel:
        run_id = request_form.get("run_id") or f"run.{datetime.now():%Y-%m-%d.%H-%M-%S}"
        files_path = Path(config.STORAGE_PATH) / run_id
        input_sources = [str(file) for file in files_path.iterdir() if file.is_file()] if files_path.is_dir() else []

        return cls(
            id=run_id,
            name=request_form.get("run_name", ""),
            processing_library=request_form.get("processing_library", ""),
            ai_provider=request_form.get("ai_provider", ""),
            ai_model=request_form.get("ai_model", ""),
            input_sources=input_sources,
            prompt=request_form.get("processing_prompt", config.DEFAULT_PROMPT),
        )

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

