from common.config.constants import REPO_PATH_WEB_DATA_QUERIES_JSON
from common.storage.example_queries import parse_data


def test_parse_file() -> None:
    with open(REPO_PATH_WEB_DATA_QUERIES_JSON) as f:
        text = f.read()
        p = parse_data(text)
        assert p is not None
