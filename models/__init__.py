from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List


@dataclass
class Document:
    id: str
    doi: str
    url: str = None
    title: str = None
    authors: List[str] = field(default_factory=list)
    content: str = None
    abstract: str = None
    citations: int = None
    source: str = None
    date: datetime = None
    references: List[str] = field(default_factory=list)

    def asdict(self) -> Dict:
        return asdict(self)

    @property
    def error(self) -> str:
        return self.__error if hasattr(self, "__error") else None

    @error.setter
    def error(self, error_message: str):
        self.__error = error_message
