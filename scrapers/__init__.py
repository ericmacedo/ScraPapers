import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from urllib.parse import urlparse


class Scraper(ABC):
    def __init__(self, doi: str):
        doi = doi.strip()
        self._id = hashlib.md5(doi.encode("utf-8"))
        self._doi = doi

    def is_domain_supported(self) -> bool:
        domain = urlparse(self.url).netloc
        return any(sup in domain for sup in self.SUPPORTED_DOMAINS)

    @property
    def id(self) -> str:
        return self._id

    @property
    def url(self) -> str:
        return self._url if self._url else None

    @property
    def doi(self) -> str:
        return self._doi

    @property
    @abstractmethod
    def SUPPORTED_DOMAINS(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def authors(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def content(self) -> str:
        pass

    @property
    @abstractmethod
    def abstract(self) -> str:
        pass

    @property
    @abstractmethod
    def citations(self) -> int:
        pass

    @property
    @abstractmethod
    def source(self) -> str:
        pass

    @property
    @abstractmethod
    def date(self) -> datetime:
        pass

    @property
    @abstractmethod
    def references(self) -> List[str]:
        pass
