from pathlib import PosixPath
from typing import List

from utils.text import extract_doi
from pandas import Series, read_csv, NA


def doi_list_from_txt(path: PosixPath) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        txt: str = f.read()

    return [*set(extract_doi(txt))]


def doi_list_from_tabular(path: PosixPath, sep: str, column: str) -> List[str]:
    series: Series = read_csv(path, sep=sep, encoding="utf-8",
                              usecols=[column], na_values=NA).squeeze()

    return series.dropna().apply(str.strip).astype(str).unique().tolist()
