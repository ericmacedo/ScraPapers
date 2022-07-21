import os
import re
from datetime import datetime
from typing import List

import requests

from scrapers import IScraperStrategy
from utils.pdf import PDF
from utils.text import fix_text_wraps, extract_name
from webdriver import WebDriver


class ACMScraper(IScraperStrategy):
    @classmethod
    def SUPPORTED_DOMAINS(cls) -> List[str]:
        return [
            "dl.acm.org"
        ]

    def __init__(self, browser: WebDriver):
        self.__webdriver: WebDriver = browser

    @property
    def title(self) -> str:
        return self.__webdriver.find_element("h1.citation__title").text

    @property
    def authors(self) -> List[str]:
        authors = [
            extract_name(i.text)
            for i in self.__webdriver.find_elements("span.loa__author-name")
        ]
        return authors if any(authors) else None

    @property
    def content(self) -> str:
        self.__webdriver.click_element("a.pdf-file a")
        self.__webdriver.wait_for_download_queue()

        pdf_path = self.__webdriver.download_list()[0]

        pdf = PDF(path=pdf_path, remove_css_selectors="div.annotation")

        self.__webdriver.back()
        os.remove(pdf_path)

        return fix_text_wraps(pdf.full_text)

    @property
    def abstract(self) -> str:
        return self.__webdriver.find_element(".abstractInFull p").text

    @property
    def citations(self) -> int:
        citation = self.__webdriver.find_element("span.citation").text

        match = re.match(r"(\d+)\nCitation.?", citation, re.IGNORECASE)
        return int(match.group(1)) if match else None

    @property
    def source(self) -> str:
        return self.__webdriver.find_element(".issue-item__detail a").text

    @property
    def date(self) -> datetime:
        date = self.__webdriver.find_element("span.CitationCoverDate").text

        return datetime.strptime(date, "%d %B %Y") if date else None

    @property
    def references(self) -> List[str]:
        selector = ".show-more-items__btn-holder button"
        el = self.__webdriver.find_element(selector)

        if el.text == "Show All References":
            self.__webdriver.click_element(
                selector=selector,
                wait_for_selector=".references__item.js--toggle")

        refs = self.__webdriver.find_elements(
            'li.references__item:not([id$="_copy"]) span.references__note')
        return [ref.text for ref in refs]


def get_strategy() -> IScraperStrategy:
    return ACMScraper
