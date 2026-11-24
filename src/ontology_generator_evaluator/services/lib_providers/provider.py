from typing import Protocol


class LibProvider(Protocol):
    def split_text(self, text: str) -> list[str]: ...
