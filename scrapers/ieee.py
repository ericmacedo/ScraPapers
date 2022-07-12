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


class IEEEScraper(Scraper):
    def __init__(self, doi: str):
        super(IEEEScraper, self).__init__(doi)

        if (request := requests.get(f"https://doi.org/{self.doi}")).ok:
            self._url = request.url

            if not self.is_domain_supported():
                raise Exception(f"Unsupported url: {self.url}")

            self.__webdriver = WebDriver()
            self.__webdriver.get(request.url)
        else:
            raise Exception(f"Request error (Code {request.status_code})")

    @property
    def __is_content_html(self) -> bool:
        return any(self.__webdriver.find_elements(".section"))

    @property
    def SUPPORTED_DOMAINS(self) -> List[str]:
        return [
            "ieeexplore.ieee.org"
        ]

    @property
    def title(self) -> str:
        return self.__webdriver.find_element(".document-title").text

    @property
    def authors(self) -> List[str]:
        authors = [
            strip_name(i.text)
            for i in self.__webdriver.find_elements(".authors-info")
        ]
        return authors if any(authors) else None

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

            return "\n".join(sections.values())
        else:
            self.__webdriver.click_element(
                ".stats-document-lh-action-downloadPdf_2")

            pdf_path = get_latest_pdf_path(self.__webdriver.download_dir)

            with open(pdf_path, "rb") as f_pdf:
                pdf_str = pdf_to_string(f_pdf)

            os.remove(pdf_path)
            self.__webdriver.back()

            pdf_str = re.sub(
                r"(?!.+)(?:\n*Authorized licensed use limited to:.+\n*)(?<!.)",
                r" ", pdf_str)
            pdf_str = fix_text_wraps(pdf_str)

            return pdf_str

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
