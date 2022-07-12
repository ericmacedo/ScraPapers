from asyncio import selector_events
import re
from datetime import datetime
from typing import List

import requests
from selenium.webdriver.common.by import By

from scrapers import Scraper
from utils import get_latest_pdf_path
from utils.pdf import pdf_to_string
from utils.text import strip_name, fix_text_wraps
from webdriver import WebDriver

import os


class ACMScraper(Scraper):
    def __init__(self, doi: str):
        super(ACMScraper, self).__init__(doi)

        if (request := requests.get(f"https://doi.org/{self.doi}")).ok:
            self._url = request.url

            if not self.is_domain_supported():
                raise Exception(f"Unsupported url: {self.url}")

            self.__webdriver = WebDriver()
            self.__webdriver.get(request.url)
        else:
            raise Exception(f"Request error (Code {request.status_code})")

    @property
    def SUPPORTED_DOMAINS(self) -> List[str]:
        return [
            "dl.acm.org"
        ]

    @property
    def title(self) -> str:
        return self.__webdriver.find_element("h1.citation__title").text

    @property
    def authors(self) -> List[str]:
        authors = [
            strip_name(i.text)
            for i in self.__webdriver.find_elements("span.loa__author-name")
        ]
        return authors if any(authors) else None

    @property
    def content(self) -> str:
        self.__webdriver.click_element(".pdf-file a")

        pdf_path = get_latest_pdf_path(self.__webdriver.download_dir)

        with open(pdf_path, "rb") as f_pdf:
            pdf_str = pdf_to_string(f_pdf)

        os.remove(pdf_path)
        self.__webdriver.back()
        pdf_str = fix_text_wraps(pdf_str)

        return pdf_str

    @property
    def abstract(self) -> str:
        return self.__webdriver.find_element(".abstractInFull p").text

    @property
    def citations(self) -> int:
        citation = self.__webdriver.find_element("span.citation").text

        match = re.match(r"(\d+)\nCitation", citation)
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
                wait_for_selector=".references__item js--toggle")

        refs = self.__webdriver.find_elements(
            'li.references__item:not([id$="_copy"]) span.references__note')
        return [ref.text for ref in refs]
