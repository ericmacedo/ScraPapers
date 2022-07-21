import re
from datetime import datetime
from typing import List

from selenium.webdriver.common.by import By

from scrapers import IScraperStrategy
from utils.text import fix_text_wraps, extract_name
from webdriver import WebDriver
from webdriver.utils import get_text_from_element


class WileyScraper(IScraperStrategy):
    @classmethod
    def SUPPORTED_DOMAINS(cls) -> List[str]:
        return [
            "onlinelibrary.wiley.com"
        ]

    def __init__(self, browser: WebDriver):
        self.__webdriver: WebDriver = browser

    @property
    def title(self) -> str:
        return self.__webdriver.get_metadata(name="citation_title")

    @property
    def authors(self) -> List[str]:
        authors = [
            extract_name(i)
            for i in self.__webdriver.get_metadata(name="citation_author")]
        return authors if any(authors) else None

    @property
    def content(self) -> str:
        sections = {}
        article = self.__webdriver.find_element(
            "section.article-section__full")
        for section in article.find_elements(By.CSS_SELECTOR,
                                             ":scope > section.article-section__content," +
                                             "section.article-section__sub-content"):
            title = section.find_element(By.CSS_SELECTOR, "h2, h3, h4").text
            sections[f"{title}"] = " ".join([
                i.text for i in section.find_elements(
                    By.CSS_SELECTOR, ":not(h2, h3, h4)")
            ]).strip()
        return fix_text_wraps(" ".join(sections.values())) if sections else None

    @property
    def abstract(self) -> str:
        return "\n".join([
            i.text
            for i in self.__webdriver.find_elements(
                "section.article-section__abstract p")
        ])

    @property
    def citations(self) -> int:
        count = self.__webdriver.find_element("div.cited-by-count a")
        return int(count.text) if count else None

    @property
    def source(self) -> str:
        return self.__webdriver.get_metadata(name="citation_journal_title")

    @property
    def date(self) -> datetime:
        date = self.__webdriver.get_metadata(name="citation_online_date")

        return datetime.strptime(date, "%Y/%m/%d") if date else None

    @property
    def references(self) -> List[str]:
        return [
            re.sub(r"(?P<ref>^.+\.).+$", r"\g<ref>", get_text_from_element(i))
            for i in self.__webdriver.find_elements(
                "section#references-section li[data-bib-id]")]


def get_strategy() -> IScraperStrategy:
    return WileyScraper
