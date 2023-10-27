from common.config.constants import REPO_PATH_WEB_DATA_DISPUTED_JSON
from common.storage.disputed_results import parse_data


def test_parse_file() -> None:
    with open(REPO_PATH_WEB_DATA_DISPUTED_JSON) as f:
        text = f.read()
        p = parse_data(text)
        assert p is not None
