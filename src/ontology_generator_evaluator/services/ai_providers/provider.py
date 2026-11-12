from typing import Protocol


class AIProvider(Protocol):

    def get_models(self) -> list[dict]:
        ...

    def generate(self, prompt: str) -> str:
        ...
