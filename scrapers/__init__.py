import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from importlib.util import module_from_spec, spec_from_file_location
import pathlib
from typing import Dict, Iterable, List
from urllib.parse import urlparse

import requests

from webdriver import WebDriver

from models import Document
import re


class IScraperStrategy(ABC):
    @classmethod
    @abstractmethod
    def SUPPORTED_DOMAINS(cls) -> List[str]:
        pass

    @abstractmethod
    def __init__(self, browser: WebDriver):
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


class Scraper:
    """
    Strategy design pattern
    - Concrete strategies must extend IScraperStrategy
    """
    @classmethod
    def AVAILABLE_STRATEGIES(cls) -> Dict[str, IScraperStrategy]:
        def load_strategy_from_path(name: str, path: str) -> IScraperStrategy:
            spec = spec_from_file_location(name, path)
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

        strategies = {
            f"{file.name.rstrip('.py')}": f"{file}"
            for file in pathlib.Path(__file__).absolute().parent.glob(
                '**/*.py'
            ) if re.match(r"^[A-Za-z]+\.py", f"{file.name}")}

        return {
            f"{name}": load_strategy_from_path(name, path).get_strategy()
            for name, path in strategies.items()}

    def __init__(self):
        self.__webdriver: WebDriver = WebDriver()
        self.__strategy: IScraperStrategy = None

        self.__available_strategies = {
            f"{name}": strategy(self.__webdriver)
            for name, strategy in Scraper.AVAILABLE_STRATEGIES().items()
        }

    def __set_strategy(self, url: str) -> bool:
        for strategy in self.__available_strategies.values():
            if urlparse(url).netloc in strategy.SUPPORTED_DOMAINS():
                self.__strategy = strategy
                return True
        return False

    def get(self, doi_list: Iterable[str] | str) -> List[Document] | Document:
        if isinstance(doi_list, str):
            doi_list = [doi_list]

        documents: List[Document] = []
        for doi in doi_list:
            doc = dict(
                id=hashlib.md5(doi.encode("utf-8")).hexdigest(),
                doi=doi.strip())
            doc_error = None

            doi_url = f"https://doi.org/{doc['doi']}"
            if (request := requests.get(doi_url)).ok:
                doc['url'] = request.url

                if self.__set_strategy(doc['url']):
                    self.__webdriver.get(doc['url'])
                    doc.update(dict(
                        title=self.__strategy.title,
                        authors=self.__strategy.authors,
                        content=self.__strategy.content,
                        abstract=self.__strategy.abstract,
                        citations=self.__strategy.citations,
                        source=self.__strategy.source,
                        date=self.__strategy.date,
                        references=self.__strategy.references))
                else:
                    doc_error = f"Unsupported url: {doc['url']}"
            else:
                doc_error = f"Request error (Code {request.status_code})"

            doc = Document(**doc)
            if doc_error:
                doc.error = doc_error
            documents.append(doc)

        return documents
