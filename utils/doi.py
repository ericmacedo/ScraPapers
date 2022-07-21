import re
from hashlib import md5
from pathlib import Path
from typing import List

from pandas import NA, Series, read_csv


def doi_to_md5(doi: str) -> str:
    return md5(doi.encode("utf-8")).hexdigest()


def doi_list_from_txt(path: Path) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        txt: str = f.read()

    return [*set(extract_doi(txt))]


def doi_list_from_tabular(path: Path, sep: str, column: str) -> List[str]:
    series: Series = read_csv(path, sep=sep, encoding="utf-8",
                              usecols=[column], na_values=NA).squeeze()

    return series.dropna().apply(str.strip).astype(str).unique().tolist()


def extract_doi(s: str) -> List[str]:
    return re.findall(r"(?P<doi>\d+\.\d+/\S+\b)", s, re.MULTILINE)
