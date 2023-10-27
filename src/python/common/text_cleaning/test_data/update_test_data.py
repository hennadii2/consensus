"""

Updates expected output of configured test data files with latest text cleaning.

Example usage:
  ./pants run src/python/common/tetx_cleaning/test_data:update_test_data

"""
import glob
import re
from pathlib import Path

from common.text_cleaning.base_text_cleaner import BaseTextCleaner

TEST_DATA_BASE_PATH = "src/python/common/text_cleaning/test_data"
TEST_DATA_PATTERNS = [
    "raw_semantic_scholar_s2-corpus-000_2022-01-01/*_raw",
]


def update_test_data(input_path_pattern: str):
    raw_files = glob.glob(input_path_pattern)
    base_text_cleaner = BaseTextCleaner()
    for raw_file in raw_files:
        raw_text = Path(raw_file).read_text()
        cleaned_text = base_text_cleaner.clean_text(raw_text)
        cleaned_file = re.sub(r"_raw$", "_cleaned", raw_file)
        Path(cleaned_file).write_text(cleaned_text)


if __name__ == "__main__":
    for pattern in TEST_DATA_PATTERNS:
        update_test_data(input_path_pattern=f"{TEST_DATA_BASE_PATH}/{pattern}")
