from datetime import datetime
from typing import List

from selenium.webdriver.common.by import By

from scrapers import IScraperStrategy
from common.utils.text import fix_text_wraps, extract_name
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
    def title(self) -> str:
        return self.__webdriver.get_metadata(name="dc.title")

    @property
    def authors(self) -> List[str]:
        authors = [
            extract_name(i.text)
            for i in self.__webdriver.find_elements(
                "ul.c-article-author-list li.c-article-author-list__item")
        ]
        return authors if any(authors) else None

    @property
    def content(self) -> str:
        sections = {}
        for section in self.__webdriver.find_elements("article section"):
            title = section.get_attribute("data-title")
            sections[f"{title}"] = " ".join([
                i.text for i in section.find_elements(
                    By.CSS_SELECTOR, "div.c-article-section :not(h2, h3, h4)")
            ])
        return fix_text_wraps(" ".join(sections.values())) if sections else None

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
        return datetime.strptime(
            self.__webdriver.get_metadata(name="dc.date"), "%Y-%m-%d")

    @property
    def references(self) -> List[str]:
        return [
            ref.text for ref in self.__webdriver.find_elements(
                'p.c-article-references__text')]


def get_strategy() -> IScraperStrategy:
    return BMCScraper
