import re
from abc import ABC, abstractmethod
from datetime import datetime
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Coroutine, Dict, Generator, Iterable, List
from urllib.parse import urlparse

import pandas as pd
from tqdm import tqdm

from common.models.corpus import Corpus
from common.models.document import Document
from common.utils.text import extract_ngrams
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
            for file in Path(__file__).absolute().parent.glob(
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


class ScrapperManager:
    def __init__(self, doi_list: Iterable[str] = [],
                 output_dir: List[str] = [".", "output"]) -> None:
        self.__scraper = Scraper()

        self.__doi_list = doi_list

        # Output directory
        self.__output_dir = Path(*output_dir).resolve()
        self.__corpus_dir = self.__output_dir.joinpath("corpus")
        self.__corpus_dir.mkdir(parents=True, exist_ok=True)

        self.__vocab_dict = {
            "path_or_buf": self.__output_dir.joinpath("vocab.tsv"),
            "encoding": "utf-8", "sep": "\t", "index": False, "header": False}

        self.corpus: Corpus = Corpus()

        self.__build_corpus()

    @property
    def documents(self) -> Generator[Document, None, None]:
        for doc in self.corpus.index:
            yield Document.load(self.__corpus_dir.joinpath(f"{doc}.json"))

    @property
    def __pending(self) -> List[str]:
        if not self.documents:
            return self.__doi_list
        return [*set(self.__doi_list) - set(self.corpus["doi"])]

    def __build_corpus(self):
        if self.__pending:
            for doc in self.__scraper.get(self.__pending):
                doc.save(self.__corpus_dir)

            vocab: pd.DataFrame = extract_ngrams(self.corpus["content"])
            vocab.to_csv(**self.__vocab_dict)
