from typing import Protocol
from pydantic import BaseModel, Field


class LibProvider(Protocol):

    ontology_schema: BaseModel

    def chunk_text(self, text: str, chunk_size: int) -> list[str]:
        ...

    def set_schema(self, ontology_schema: BaseModel) -> None:
        self.ontology_schema = ontology_schema

    def process_input(self, input_sources: list[str], prompt: str) -> dict:
        ...