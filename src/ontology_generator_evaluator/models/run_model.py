from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import config

config.load_config()


@dataclass
class RunModel:
    id: str
    name: str
    processing_library: str
    ai_provider: str
    ai_model: str
    input_sources: list[str] = field(default_factory=list)
    prompt: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> RunModel:
        return cls(
            id=data.get("id", ""),
            name=data["name"],
            processing_library=data["processing_library"],
            ai_provider=data["ai_provider"],
            ai_model=data["ai_model"],
            input_sources=list(data.get("input_sources", [])),
            prompt=data.get("prompt", ""),
        )

    @classmethod
    def from_request(cls, request_form: Mapping[str, str]) -> RunModel:
        run_id = request_form.get("run_id") or f"run.{datetime.now():%Y-%m-%d.%H-%M-%S}"
        files_path = Path(config.STORAGE_PATH) / run_id
        input_sources = (
            [str(file) for file in files_path.iterdir() if file.is_file()]
            if files_path.is_dir()
            else []
        )

        return cls(
            id=run_id,
            name=request_form.get("run_name", ""),
            processing_library=request_form.get("processing_library", ""),
            ai_provider=request_form.get("ai_provider", ""),
            ai_model=request_form.get("ai_model", ""),
            input_sources=input_sources,
            prompt=request_form.get("processing_prompt", ""),
        )