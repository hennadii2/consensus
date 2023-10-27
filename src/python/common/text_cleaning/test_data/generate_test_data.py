"""

Adds test data from an original provider file to the test data directory.
This currently works for semantic scholar only.

NOTE: Use update_test_data.py if you want to update _cleaned files after making
changes to text cleaning code.

Example usage:
  ./pants run src/python/common/tetx_cleaning/test_data:generate_test_data

"""
import gzip
import os
from pathlib import Path

from common.config.constants import REPO_PATH_MOCK_DATA_SEMANTIC_SCHOLAR
from common.ingestion.extract import (
    extract_metadata_and_abstract,
    filter_metadata_for_ingestion,
    filter_metadata_for_product,
)
from common.text_cleaning.base_text_cleaner import BaseTextCleaner
from paper_metadata_pb2 import PaperProvider

NUMBER_TEST_DATA_FILES_TO_ADD = 30

OUTPUT_PATH = "src/python/common/text_cleaning/test_data"


def generate_test_data(
    input_path: str,
    max_count: int,
):

    mock_data_path = Path(input_path).stem
    output_dir = f"{OUTPUT_PATH}/{mock_data_path}"
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    base_text_cleaner = BaseTextCleaner()

    count = 0
    with gzip.open(input_path, "rt") as mock_data_file:
        for index, line in enumerate(mock_data_file):
            if count >= max_count:
                break

            metadata, abstract = extract_metadata_and_abstract(
                PaperProvider.SEMANTIC_SCHOLAR, line
            )

            # Filter for ingestion requirements
            try:
                filter_metadata_for_ingestion(metadata)
            except Exception:
                continue

            # Filter for product requirements
            try:
                filter_metadata_for_product(metadata)
            except Exception:
                continue

            test_data_fields = [
                ("title", str(metadata.title)),
                ("abstract", str(abstract)),
            ]

            base_filename = f"{output_dir}/{metadata.provider_id}"
            for test_data_field in test_data_fields:
                name, text = test_data_field
                cleaned_text = base_text_cleaner.clean_text(text)
                Path(f"{base_filename}_{name}_raw").write_text(text)
                Path(f"{base_filename}_{name}_cleaned").write_text(cleaned_text)

            count += 1


if __name__ == "__main__":
    generate_test_data(
        input_path=REPO_PATH_MOCK_DATA_SEMANTIC_SCHOLAR,
        max_count=NUMBER_TEST_DATA_FILES_TO_ADD,
    )
