import pathlib
from contextlib import contextmanager
from sys import platform
from typing import Any, List, Tuple

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

from collections import namedtuple

ResponseStatus = namedtuple("ResponseStatus", ["status", "code"])


class WebDriver:
    def __init__(self):
        self.__geckodriver = pathlib.Path(__file__).parent.absolute().joinpath(
            "geckodriver"
        ).resolve()

        self.__download_dir = pathlib.Path(
            ".").absolute().joinpath(".data").resolve()
        self.__download_dir.mkdir(parents=True, exist_ok=True)

        self.__options = FirefoxOptions()
        self.__options.add_argument("--headless")

        preferences = [
            ("browser.download.folderList", 2),
            ("browser.download.dir", f"{self.__download_dir}"),
            ("browser.download.useDownloadDir", True),
            ("browser.helperApps.neverAsk.saveToDisk", "application/pdf"),
            ("pdfjs.disabled", True)]
        for pref in preferences:
            self.__options.set_preference(*pref)

        self.__browser = None

    def __connect(self):
        self.__browser = webdriver.Firefox(
            executable_path=f"{self.__geckodriver}.{self.__driver_ext()}",
            service_log_path=f"{self.__geckodriver}.log",
            options=self.__options)

    def __disconnect(self):
        if self.__browser:
            self.__browser.quit()
            del self.__browser
            self.__browser = None

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

    @property
    def download_dir(self) -> str:
        return self.__download_dir

    @contextmanager
    def get(self, url: str) -> None:
        self.__connect()
        self.__browser.get(url)

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
            WebDriverWait(self.__browser, timeout=30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, wait_for_selector)))

    # Browser navigation
    def back(self) -> None:
        self.__browser.back()
