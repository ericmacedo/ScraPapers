import time
from collections import namedtuple
from contextlib import contextmanager
from os.path import getctime
from pathlib import Path
from sys import platform
from typing import List

from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException,
                                        TimeoutException)
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

ResponseStatus = namedtuple("ResponseStatus", ["status", "code"])


class WebDriver:
    def __init__(self):
        self.__geckodriver = Path(__file__).parent.absolute().joinpath(
            "geckodriver"
        ).resolve()

        self.__download_dir = Path(".").absolute().joinpath(".data").resolve()
        self.__download_dir.mkdir(parents=True, exist_ok=True)

        self.__options = FirefoxOptions()
        self.__options.add_argument("--headless")

        preferences = [
            ("dom.webdriver.enabled", False),

            # Downlaod settings
            ("browser.download.folderList", 2),
            ("browser.download.dir", f"{self.__download_dir}"),
            ("browser.download.useDownloadDir", True),
            ("browser.helperApps.neverAsk.saveToDisk", "application/pdf"),
            ("pdfjs.disabled", True),

            # disable prefetching
            ("network.dns.disablePrefetch", True),
            ("network.prefetch-next", False),

            # disable OpenH264 codec downloading
            ("media.gmp-gmpopenh264.enabled", False),
            ("media.gmp-manager.url", ""),

            # disable experiments
            ("experiments.enabled", False),
            ("experiments.supported", False),
            ("experiments.manifest.uri", ""),

            # disable telemetry
            ("toolkit.telemetry.enabled", False),
            ("toolkit.telemetry.unified", False),
            ("toolkit.telemetry.archive.enabled", False),
            ("browser.contentblocking.category", "strict"),

            # disable health reports
            ("datareporting.healthreport.service.enabled", False),
            ("datareporting.healthreport.uploadEnabled", False),
            ("datareporting.policy.dataSubmissionEnabled", False)]

        for pref in preferences:
            self.__options.set_preference(*pref)

        self.__browser = None

    def __connect(self):
        self.__browser = webdriver.Firefox(
            executable_path=f"{self.__geckodriver}.{self.__driver_ext()}",
            service_log_path=f"{self.__geckodriver}.log",
            capabilities=DesiredCapabilities.FIREFOX,
            options=self.__options)

    def __disconnect(self):
        if self.__browser:
            self.__browser.quit()
            del self.__browser
            self.__browser = None

    def wait_for_download_queue(self, timeout: int = 60) -> Path:
        initial_pdf_count = len([*Path(self.__download_dir).glob("*.pdf")])

        for _ in range(timeout):
            current_pdf_count = len([*Path(self.__download_dir).glob("*.pdf")])
            part_count = len([*Path(self.__download_dir).glob("*.part")])
            if part_count == 0 and current_pdf_count > initial_pdf_count:
                break
            time.sleep(1)
        else:
            raise TimeoutError(
                f"No download queue was detected within {timeout} seconds")

        return self.download_list()[0]

    def __del__(self):
        self.__disconnect()

    @property
    def url(self) -> str:
        if not self.__browser or self.__browser.current_url == "about:blank":
            return None
        return self.__browser.current_url

    @property
    def response(self) -> ResponseStatus:
        if not self.__browser:
            return ResponseStatus(False, 500)

        request = next(filter(
            lambda i: (
                self.__browser.current_url in i.url and
                i.response and i.response.status_code < 400
            ), self.__browser.requests), None)
        return ResponseStatus(True, request.response.status_code)

    def download_list(self, n: int = 1, descending: bool = True) -> List[str]:
        return sorted(
            Path(self.__download_dir).absolute().glob("*.pdf"),
            key=getctime, reverse=descending)[:n]

    @contextmanager
    def get(self, url: str) -> None:
        self.__connect()
        self.__browser.get(url)
        self.wait_for_url_change()

        yield self

        self.__disconnect()

    def __driver_ext(self) -> str:
        if platform == "darwin":
            ext = "osx"
        elif platform == "cygwin" or platform == "win32":
            ext = "exe"
        else:
            ext = "linux"

        return ext

    def get_metadata(self, **kwargs) -> str:
        if not kwargs:
            return None

        selector: str = "meta"
        for field, value in kwargs.items():
            selector += f'[{field}="{value}"]'
        return self.__browser.find_element(
            By.CSS_SELECTOR, selector).get_attribute("content")

    def find_element(self, selector: str) -> WebElement:
        try:
            el = self.__browser.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            el = None
        finally:
            return el

    def find_elements(self, selector: str) -> List[WebElement]:
        return self.__browser.find_elements(By.CSS_SELECTOR, selector)

    def click_element(self, selector: str, wait_for_selector: str = None) -> None:
        if el := self.find_element(selector):
            self.__browser.execute_script("arguments[0].click();", el)

        if wait_for_selector:
            self.wait_for_element(wait_for_selector)

    def wait_for_element(self, selector: str, timeout: int = 10) -> WebElement:
        time.sleep(1)
        return WebDriverWait(self.__browser, timeout, ignored_exceptions=[
            StaleElementReferenceException, NoSuchElementException
        ]).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

    def wait_for_elements(self, selector: str, timeout: int = 10) -> List[WebElement]:
        time.sleep(1)
        return WebDriverWait(self.__browser, timeout, ignored_exceptions=[
            StaleElementReferenceException, NoSuchElementException
        ]).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))

    def wait_for_url_change(self, timeout: int = 10) -> None:
        try:
            WebDriverWait(self.__browser, timeout).until(
                EC.url_changes(self.__browser.current_url))
        except TimeoutException:
            pass

    # Browser navigation
    def back(self) -> None:
        self.__browser.back()
