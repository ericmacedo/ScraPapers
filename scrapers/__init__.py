import pathlib
import re
from abc import ABC, abstractmethod
from datetime import datetime
from importlib.util import module_from_spec, spec_from_file_location
from typing import Dict, Generator, Iterable, List
from urllib.parse import urlparse

from tqdm import tqdm

from models import Document
from utils.doi import doi_to_md5
from webdriver import ResponseStatus, WebDriver


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

    def asdict(self) -> Dict:
        return dict(
            title=self.title,
            authors=self.authors,
            content=self.content,
            abstract=self.abstract,
            citations=self.citations,
            source=self.source,
            date=self.date,
            references=self.references)


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
                "*.py"
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

    def __del__(self):
        del self.__webdriver

    def __set_strategy(self, url: str) -> bool:
        for strategy in self.__available_strategies.values():
            domains = strategy.SUPPORTED_DOMAINS()
            netloc: str = urlparse(url).netloc
            if any(filter(lambda i: i in netloc, domains)):
                self.__strategy = strategy
                return True
        return False

    def get(self, doi_list: Iterable[str] | str) -> Generator[Document, None, None]:
        if isinstance(doi_list, str):
            doi_list = [doi_list]

        with tqdm(total=len(doi_list)) as pbar:
            for doi in doi_list:
                doi = doi.strip()
                doc = dict(id=doi_to_md5(doi), doi=doi)
                doc_error = None

                pbar.set_description(f"Processing DOI ({doc['doi']})")
                with self.__webdriver.get(f"https://doi.org/{doc['doi']}"):
                    response: ResponseStatus = self.__webdriver.response
                    if response.status:
                        doc['url'] = self.__webdriver.url

                        if self.__set_strategy(doc['url']):
                            doc.update(self.__strategy.asdict())
                        else:
                            doc_error = f"Unsupported url: {doc['url']}"
                    else:
                        doc_error = f"Request error (Code {response.code})"

                doc = Document(**doc)
                if doc_error:
                    doc.error = doc_error
                pbar.update(1)

                yield doc
