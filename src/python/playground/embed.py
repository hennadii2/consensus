import argparse

from common.models.similarity_search_embedding import (
    encode_similarity_search_embedding,
    initialize_similarity_search_embedding_model,
)

EMBEDDING_MODEL = initialize_similarity_search_embedding_model()


def _parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        "-q",
        required=True,
        type=str,
        help="Query to embed",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)
    embedding = encode_similarity_search_embedding(EMBEDDING_MODEL, args.query)
    print(embedding)


if __name__ == "__main__":
    main()
