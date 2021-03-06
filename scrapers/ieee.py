import os
import re
from datetime import datetime
from typing import List
from urllib import response

import requests
from selenium.webdriver.common.by import By

from scrapers import IScraperStrategy
from utils.pdf import PDF
from utils.text import extract_name, fix_text_wraps
from webdriver import WebDriver


class IEEEScraper(IScraperStrategy):
    @classmethod
    def SUPPORTED_DOMAINS(cls) -> List[str]:
        return [
            "ieeexplore.ieee.org"
        ]

    def __init__(self, browser: WebDriver):
        self.__webdriver: WebDriver = browser

    @property
    def __is_content_html(self) -> bool:
        return any(self.__webdriver.find_elements(".section"))

    @property
    def title(self) -> str:
        return self.__webdriver.find_element(".document-title").text

    @property
    def authors(self) -> List[str]:
        id = "#authors-header"
        el = self.__webdriver.find_element(id)

        if el.get_attribute("aria-expanded") == "false":
            self.__webdriver.click_element(id, ".authors-accordion-container")

        return [
            extract_name(i.text.split("\n")[0])
            for i in self.__webdriver.find_elements(
                ".authors-accordion-container")]

    @property
    def content(self) -> str:
        sections = {}

        sections["abstract"] = self.abstract

        if self.__is_content_html:
            for section in self.__webdriver.find_elements(".section"):
                title = section.find_element(By.TAG_NAME, "h2").text.strip()
                paragraphs = [
                    paragraph.text.strip()
                    for paragraph in section.find_elements(By.TAG_NAME, "p")]
                sections[f"{title.lower()}"] = "\n".join(paragraphs)

            return fix_text_wraps(" ".join(sections.values()))
        else:
            self.__webdriver.click_element(
                "a.stats-document-lh-action-downloadPdf_2")

            pdf_path = self.__webdriver.wait_for_download_queue()

            pdf = PDF(path=pdf_path, remove_css_selectors="div.annotation")

            self.__webdriver.back()
            os.remove(pdf_path)

            return fix_text_wraps(pdf.full_text)

    @property
    def abstract(self) -> str:
        return self.__webdriver.find_element(
            ".abstract-text"
        ).text.replace("Abstract:\n", "")

    @property
    def citations(self) -> int:
        metrics = self.__webdriver.find_element(
            ".document-banner-metric-container"
        ).text

        match = re.match(r"(\d+)\nPaper\nCitations", metrics)
        return int(match.group(1)) if match else None

    @property
    def source(self) -> str:
        return self.__webdriver.find_element(
            ".stats-document-abstract-publishedIn"
        ).find_element(By.TAG_NAME, "a").text

    @property
    def date(self) -> datetime:
        if date := self.__webdriver.find_element(".doc-abstract-pubdate"):
            date = date.text.replace("Date of Publication: ", "")
        elif date := self.__webdriver.find_element(".doc-abstract-confdate"):
            date = date.text.replace("Date of Conference: ", "")
            date = re.sub(r"(?:(?P<date>\d{1,2})-\d{1,2})", r"\g<date>", date)
        else:
            date = None

        return datetime.strptime(date, "%d %B %Y") if date else None

    @property
    def references(self) -> List[str]:
        id = "#references-header"
        el = self.__webdriver.find_element(id)

        if el.get_attribute("aria-expanded") == "false":
            self.__webdriver.click_element(
                "#references-header", ".reference-container")

        refs = [
            ref.text for ref in self.__webdriver.find_elements(
                ".reference-container"
            ) if ref.text]

        return [
            re.sub(
                r"(?:^\d+\.\n(?P<ref>.+\b\.)(\n.+)*)",
                r"\g<ref>", ref
            ) for ref in refs
        ]


def get_strategy() -> IScraperStrategy:
    return IEEEScraper
