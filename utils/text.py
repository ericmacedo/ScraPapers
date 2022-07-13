import re


def strip_name(s: str) -> str:
    s = re.sub(
        r"(?P<last>[A-Z][a-z]+)\,\s?(?P<first>([A-Z]([a-z]+|\.?)\ ?)+)",
        r"\g<first> \g<last>", s)
    s = re.sub(
        r"(?:(?P<name>([A-Z]([a-z]+|\.?)\s?)+\b)\s?.*)",
        r"\g<name>", s)
    return s


def fix_text_wraps(s: str) -> str:
    s = re.sub(r"-\n+", r"", s)
    s = re.sub(r"\s+", r" ", s)
    return s
