from selenium.webdriver.remote.webelement import WebElement
import re
from html import unescape


def get_text_from_element(el: WebElement) -> str:
    s = el.get_attribute("innerHTML").strip()
    s = re.sub(r"<[^<]+?>", r"", s)
    s = re.sub(r"\s+", r" ", s)
    s = unescape(s)
    return s
