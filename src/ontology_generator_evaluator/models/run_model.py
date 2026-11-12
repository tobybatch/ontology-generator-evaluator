from dataclasses import dataclass, field
from typing import List


@dataclass
class RunModel:
    name: str
    library: str
    provider: str
    model: str
    sources: List[str] = field(default_factory=list)
    prompt: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "library": self.library,
            "provider": self.provider,
            "model": self.model,
            "sources": self.sources,
            "prompt": self.prompt,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RunModel":
        return cls(
            name=data["name"],
            library=data["library"],
            provider=data["provider"],
            model=data["model"],
            sources=data.get("sources", []),
            prompt=data.get("prompt", ""),
        )