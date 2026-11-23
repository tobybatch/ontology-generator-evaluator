from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RunStatusModel:
    id: str
    run_id: str
    input_sources: list[str] = field(default_factory=list)
    source_in_progress: str = ""
    source_processed: list[str] = field(default_factory=list)

    def __init__(self, run_id: str) -> None:
        self.id = run_id
        self.run_id = run_id
        self.input_sources = []
        self.source_in_progress = ""
        self.source_processed = []

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> RunStatusModel:
        obj = cls(data.get("run_id", ""))
        obj.id = data.get("id", obj.run_id)
        obj.input_sources = list(data.get("input_sources", []))
        obj.source_in_progress = data.get("source_in_progress", "")
        obj.source_processed = list(data.get("source_processed", []))
        return obj
