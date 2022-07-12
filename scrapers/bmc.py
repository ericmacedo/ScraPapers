import re
from datetime import datetime
from typing import List
from scrapers import Scraper

import requests
from bs4 import BeautifulSoup
from utils.text import strip_name


class BMCScraper(Scraper):
    def __init__(self, doi: str):
        super(BMCScraper, self).__init__(doi)

        if (request := requests.get(f"https://doi.org/{self.doi}")).ok:
            self.__soup = BeautifulSoup(request.content, "html.parser")
            self._url = request.url

            if not self.is_domain_supported():
                raise Exception(f"Unsupported url: {self.url}")
        else:
            raise Exception(f"Request error (Code {request.status_code})")

    @property
    def CONTENT_SECTIONS(self) -> List[str]:
        return [
            'Abstract',
            'Background',
            'Methods',
            'Results',
            'Discussion',
            'Conclusions'
        ]

    @property
    def SUPPORTED_DOMAINS(self) -> List[str]:
        return [
            "biomedcentral.com"
        ]

    def __get_metadata(self, name: str) -> str:
        return self.__soup.find("meta", {"name": name}).attrs['content']

    @property
    def title(self) -> str:
        return self.__get_metadata("dc.title")

    @property
    def authors(self) -> List[str]:
        authors = [
            strip_name(i.get_text())
            for i in self.__soup.find(
                "ul", {"class": "c-article-author-list"}
            ).children
        ]
        return authors if any(authors) else None

    @property
    def content(self) -> str:
        sections = {
            f"{section.lower()}": "\n".join([
                paragraph.get_text()
                for paragraph in section.find_all("p")
            ]) for section in self.__soup.find_all("section")
            if section.get("data-title") in self.CONTENT_SECTIONS
        }
        return "\n".join(sections.values())

    @property
    def abstract(self) -> str:
        return "\n".join([
            i.get_text()
            for i in self.__soup.find(
                "div", {"id": "Abs1-content"}
            ).find_all("p")
        ])

    @property
    def citations(self) -> int:
        return None

    @property
    def source(self) -> str:
        return self.__get_metadata("dc.source")

    @property
    def date(self) -> datetime:
        return datetime.strptime(self.__get_metadata("dc.date"), "%Y-%m-%d")

    @property
    def references(self) -> List[str]:
        references = self.__soup.find(
            "ol", {"class": "c-article-references"}
        ).find_all("li")

        return [ref.find("p").get_text() for ref in references]
