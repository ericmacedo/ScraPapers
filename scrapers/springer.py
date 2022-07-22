import re
from datetime import datetime
from typing import List

from selenium.webdriver.common.by import By

from scrapers import IScraperStrategy
from utils.text import fix_text_wraps, extract_name
from webdriver import WebDriver


class SpringerScraper(IScraperStrategy):
    @classmethod
    def SUPPORTED_DOMAINS(cls) -> List[str]:
        return [
            "springer.com"
        ]

    def __init__(self, browser: WebDriver):
        self.__webdriver: WebDriver = browser

    @property
    def title(self) -> str:
        return self.__webdriver.get_metadata(name="citation_title")

    @property
    def authors(self) -> List[str]:
        authors = [
            extract_name(i.get_attribute("content"))
            for i in self.__webdriver.get_metadata(name="citation_author")]
        return authors if any(authors) else None

    @property
    def content(self) -> str:
	# TODO PDF fetching and transcription
        sections = {}
        for section in self.__webdriver.find_elements("div.c-article-body section"):
            title = section.get_attribute("data-title")
            sections[f"{title}"] = " ".join([
                i.text for i in section.find_elements(
                    By.CSS_SELECTOR, "div.c-article-section :not(h2, h3, h4)")
            ]).strip()
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
        metrics = self.__webdriver.find_element(
            "div#altmetric-container ul.c-article-metrics-bar").text
        match = re.match(r".*\n(?P<citations>\d+)\s.+", metrics)
        return int(match.group("citations")) if match else None

    @property
    def source(self) -> str:
        return self.__webdriver.get_metadata(name="citation_conference_title")

    @property
    def date(self) -> datetime:
        date = self.__webdriver.find_element("ul.c-article-identifiers time")

        if date:
            date = date.get_attribute("datetime")
            date_format = "%Y-%m-%d"
        else:
            date = self.__webdriver.get_metadata(
                name="citation_publication_date")
            date_format = "%Y"

        return datetime.strptime(date, date_format)

    @property
    def references(self) -> List[str]:
        return [
            ref.text for ref in self.__webdriver.find_elements(
                "li.c-article-references__item p.c-article-references__text")]


def get_strategy() -> IScraperStrategy:
    return SpringerScraper
