import pathlib
from sys import platform
from typing import List

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class WebDriver:
    def __init__(self):
        geckodriver_path = pathlib.Path(__file__).parent.absolute().joinpath(
            "geckodriver"
        ).resolve()

        self.__download_dir = pathlib.Path(
            ".").absolute().joinpath(".data").resolve()
        self.__download_dir.mkdir(parents=True, exist_ok=True)

        opts = FirefoxOptions()
        opts.add_argument("--headless")

        preferences = [
            ("browser.download.folderList", 2),
            ("browser.download.dir", f"{self.__download_dir}"),
            ("browser.download.useDownloadDir", True)
            ("browser.helperApps.neverAsk.saveToDisk", "application/pdf"),
            ("pdfjs.disabled", True)]
        for pref in preferences:
            opts.set_preference(*pref)

        self.__browser = webdriver.Firefox(
            executable_path=f"{geckodriver_path}.{self.__driver_ext()}",
            service_log_path=f"{geckodriver_path}.log",
            options=opts)

    def __del__(self):
        self.__browser.quit()

    @property
    def url(self) -> str:
        if self.__browser.current_url == "about:blank":
            return None
        return self.__browser.current_url

    @property
    def download_dir(self) -> str:
        return self.__download_dir

    def get(self, url: str) -> None:
        self.__browser.get(url)

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
