import glob
import os


def get_latest_pdf_path(abs_path: str) -> str:
    list_of_files = glob.glob(f"{abs_path}/*.pdf")
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file
