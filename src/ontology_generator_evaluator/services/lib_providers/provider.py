from typing import Protocol


class LibProvider(Protocol):

    def __init__(self, name: str):
        self.name = name