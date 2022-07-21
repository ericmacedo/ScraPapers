from datetime import datetime
from typing import List

from selenium.webdriver.common.by import By

from scrapers import IScraperStrategy
from utils.text import fix_text_wraps, extract_name
from webdriver import WebDriver


class ElsevierScraper(IScraperStrategy):
    @classmethod
    def SUPPORTED_DOMAINS(cls) -> List[str]:
        return [
            "sciencedirect.com",
            "linkinghub.elsevier.com"
        ]

    def __init__(self, browser: WebDriver):
        self.__webdriver: WebDriver = browser

    @property
    def title(self) -> str:
        return self.__webdriver.get_metadata(name="citation_title")

    @property
    def authors(self) -> List[str]:
        authors = [
            el for el in self.__webdriver.find_elements(
                "div#author-group a.author")]
        authors = [
            author.find_elements(By.CSS_SELECTOR, "span.content span")
            for author in authors]
        authors = [extract_name(" ".join([i.text for i in name_parts]))
                   for name_parts in authors]
        return authors if any(authors) else None

    @property
    def content(self) -> str:
        sections = {}

        for section in self.__webdriver.wait_for_elements("div#body section"):
            title = section.find_element(
                By.CSS_SELECTOR, "h2, h3, h4").text.strip()
            paragraphs = [
                paragraph
                for paragraph in section.find_elements(By.CSS_SELECTOR, "p")]
            sections[f"{title}"] = " ".join([p.text for p in paragraphs])
        return fix_text_wraps(" ".join(sections.values())) if sections else None

    @property
    def abstract(self) -> str:
        return "\n".join([
            p.text for p in self.__webdriver.find_elements("div#abstracts p")
        ])

    @property
    def citations(self) -> int:
        count = self.__webdriver.wait_for_element(
            "li.plx-citation span.pps-count")
        return int(count.text) if count else None

    @property
    def source(self) -> str:
        return self.__webdriver.get_metadata(name="citation_journal_title")

    @property
    def date(self) -> datetime:
        return datetime.strptime(
            self.__webdriver.get_metadata(name="citation_publication_date"),
            "%Y/%m/%d")

    @property
    def references(self) -> List[str]:
        return [
            fix_text_wraps(ref.text)
            for ref in self.__webdriver.wait_for_elements(
                "dl.references div.contribution")]


def get_strategy() -> IScraperStrategy:
    return ElsevierScraper
