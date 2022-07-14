import re
from datetime import datetime
from typing import Dict, List

from selenium.webdriver.common.by import By

from scrapers import IScraperStrategy
from utils.text import strip_name
from webdriver import WebDriver


class BMCScraper(IScraperStrategy):
    @classmethod
    def SUPPORTED_DOMAINS(cls) -> List[str]:
        return [
            "biomedcentral.com"
        ]

    def __init__(self, browser: WebDriver):
        self.__webdriver: WebDriver = browser

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

    def __get_metadata(self, name: str) -> str:
        return self.__webdriver.find_element(
            f'meta[name="{name}"]'
        ).get_attribute("content")

    @property
    def title(self) -> str:
        return self.__get_metadata("dc.title")

    @property
    def authors(self) -> List[str]:
        authors = [
            strip_name(i.text)
            for i in self.__webdriver.find_elements(
                "ul.c-article-author-list li.c-article-author-list__item")
        ]
        return authors if any(authors) else None

    @property
    def content(self) -> str:
        sections = {
            f"{section.get_attribute('data-title').lower()}": "\n".join([
                paragraph.text
                for paragraph in section.find_elements(By.TAG_NAME, "p")
            ]) for section in self.__webdriver.find_elements("section")
            if section.get_attribute("data-title") in self.CONTENT_SECTIONS
        }
        return "\n".join(sections.values())

    @property
    def abstract(self) -> str:
        return "\n".join([
            i.text
            for i in self.__webdriver.find_element(
                "#Abs1-content"
            ).find_elements(By.TAG_NAME, "p")
        ])

    @property
    def citations(self) -> int:
        return None

    @property
    def source(self) -> str:
        return self.__webdriver.find_element(
            '[data-test="journal-title"]'
        ).text

    @property
    def date(self) -> datetime:
        return datetime.strptime(self.__get_metadata("dc.date"), "%Y-%m-%d")

    @property
    def references(self) -> List[str]:
        return [
            ref.text for ref in self.__webdriver.find_elements(
                'p.c-article-references__text')]


def get_strategy() -> IScraperStrategy:
    return BMCScraper
