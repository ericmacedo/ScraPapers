import argparse
from pathlib import Path
from typing import List

from common.models.corpus import Corpus
from utils.doi import doi_list_from_tabular, doi_list_from_txt

import re
from pathlib import Path
import shutil

TABULAR_FORMATS = ["CSV", "TSV"]

# ============================================================================
#   Arguments
# ============================================================================
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("--name", "-n", type=str, dest="name",
                    required=True, help="Name of the dataset")
parser.add_argument("--path", "-p", type=str, dest="path",
                    help="Path to file with DOI list", required=True)
parser.add_argument("--format", "-f", type=str, dest="format",
                    choices=TABULAR_FORMATS + ["TXT"], required=True,
                    help="Format of the provided file.\n"
                    "\tCSV: columns must be separated by ','.\n"
                    "\tTSV: columns must be separated by '\\t' (tab).\n"
                    "\tTXT: DOI numbers are separated by spaces or line breaks.\n")
parser.add_argument("--column", "-c", default=None, type=str, dest="column",
                    help="Column's name with the DOI list in the tabular file")
parser.add_argument("--override", "-o", default=False, type=bool, dest="override",
                    help="Override any previous scrapping performed"
                    "(erases the 'output/' directory)")

args = parser.parse_args()

name: str = args.name

path: List[str] = args.path
file_path: str = Path(path).absolute().resolve()
if not file_path.is_file():
    print(f"No such file: {file_path}")
    exit(1)

file_format: str = args.format
column: str = args.column

override: bool = args.override

# ============================================================================
#   Extracting DOI list
# ============================================================================
doi_list: List[str] = None

if file_format in TABULAR_FORMATS:
    if not column:
        parser.error(
            "For tabular files --column is required to collect the DOI list")
        exit(1)

    sep = "," if file_format == "CSV" else "\t"

    doi_list = doi_list_from_tabular(file_path, sep, column)
else:  # TXT
    doi_list = doi_list_from_txt(file_path)

print(f"Number of valid DOI number: {len(doi_list)}")

# ============================================================================
#   Scrape
# ============================================================================

if override:
    confirm_msg = "You're about to erase all content from output. Proceed? (y/n) "
    pattern = re.compile(r"y|n", re.IGNORECASE)

    while (confirm := str(input(confirm_msg)).lower()) and not pattern(confirm):
        print("Invalid input! Must be 'y' (yes)  or 'n' (no)")

    if confirm == "n":
        print("Aborting!")
        exit(0)

    shutil.rmtree(path="output/")

corpus: Corpus = Corpus(doi_list)  # Build corpus with valid DOIs
