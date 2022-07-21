from concurrent.futures import process
from pathlib import Path
from typing import Any, Generator, Iterable, List, Tuple
import pandas as pd
from models import Document

from scrapers import Scraper
from utils import are_instances_of
from utils.doi import doi_to_md5


class Corpus:
    def __init__(self, doi_list: Iterable[str] = [], output_dir: str = "./output") -> None:
        self.__scraper = Scraper()

        self.__doi_list = doi_list

        # Output directory
        self.__output_dir = output_dir
        self.__corpus_dir = Path(
            self.__output_dir).absolute().joinpath("corpus")
        self.__corpus_dir.mkdir(parents=True, exist_ok=True)

        self.__build_corpus()
        self.__vocab_path = Path(self.__output_dir).joinpath("vocab.txt")

    @property
    def __FIELDS(self) -> List[str]:
        return [
            "id", "doi", "url", "title", "authors", "content",
            "abstract", "citations", "source", "date", "references"]

    @property
    def index(self) -> List[str]:
        return [
            doc.name.split(".")[0]
            for doc in sorted(self.__corpus_dir.glob("*.json"))]

    @property
    def documents(self) -> Generator[Document, None, None]:
        for doc in self.index:
            yield Document.load(self.__corpus_dir.joinpath(f"{doc}.json"))

    @property
    def __pending(self) -> List[str]:
        if not self.documents:
            return self.__doi_list
        return [*set(self.__doi_list) - set(self["doi"])]

    def __build_corpus(self):
        for doc in self.__scraper.get(self.__pending):
            doc.save(self.__corpus_dir)

    def __getitem__(self, indexer: str | int | slice | Tuple[str]) -> Document | List[Any]:
        if isinstance(indexer, str):
            if not indexer in self.__FIELDS:
                raise KeyError(f"Key '{indexer}' not found.")
            return [doc[indexer] for doc in self.documents]
        elif isinstance(indexer, int):
            return Document.load_asdict(
                self.__corpus_dir.joinpath(f"{self.index[indexer]}.json"))
        elif isinstance(indexer, slice):
            return [
                self.__corpus_dir.joinpath(f"{self.index[index]}.json")
                for index in self.index[indexer]]
        elif isinstance(indexer, tuple) and are_instances_of(indexer, str):
            frame = {f"key": [] for key in indexer}
            for doc in self.documents:
                for key in indexer:
                    frame[key].append(doc[key])
            return frame.values()
        else:
            raise KeyError(f"Key '{indexer}' is not a valid indexer.")

    def __corpus_updated(self) -> None:
        pass

    def append(self, doi_list: List[str] = []) -> pd.DataFrame:
        df = self.__build_dataframe(doi_list)

        self.__documents = pd.concat([self.__documents, df]).drop_duplicates()

        self.__corpus_updated()
        return self.__documents[:]
