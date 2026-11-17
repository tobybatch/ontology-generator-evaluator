from dataclasses import dataclass, field
from typing import List


@dataclass
class RunModel:
    id: str
    name: str
    library: str
    ai_provider: str
    ai_model: str
    input_sources: List[str] = field(default_factory=list)
    prompt: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "library": self.library,
            "ai_provider": self.ai_provider,
            "ai_model": self.ai_model,
            "input_sources": self.input_sources,
            "prompt": self.prompt,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RunModel":
        return cls(
            id=data.get("id", ""),
            name=data["name"],
            library=data["library"],
            ai_provider=data["ai_provider"],
            ai_model=data["ai_model"],
            input_sources=data.get("input_sources", []),
            prompt=data.get("prompt", ""),
        )