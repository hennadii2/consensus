import argparse
import json
from typing import Any

from common.search.connect import ElasticClient, SearchEnv
from elasticsearch import client


def _parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        "-q",
        required=True,
        type=str,
        help="Query to run ELSER inference on",
    )
    parser.add_argument(
        "--search-env",
        "-e",
        default="dev",
        type=str,
        help="Search environment to use",
    )
    return parser.parse_args(argv)


# currently assumes only one inference result
def _parse_infer_response(response: Any) -> dict[str, float]:
    return response["inference_results"][0]["predicted_value"]  # type: ignore [no-any-return]


def _infer(ml_client: Any, query: str) -> Any:
    return ml_client.infer_trained_model(model_id=".elser_model_1", docs=[{"text_field": query}])


def main(argv=None):
    args = _parse_args(argv)

    search_env = SearchEnv(args.search_env)
    search = ElasticClient(search_env)
    ml_client = client.MlClient(search)

    tokens = _parse_infer_response(_infer(ml_client, args.query))

    print(json.dumps(tokens, indent=2))


if __name__ == "__main__":
    main()
