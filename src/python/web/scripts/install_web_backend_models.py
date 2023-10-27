from argparse import ArgumentParser

from web.backend.app.state import initialize_models


def main(argv=None):
    """
    Initializes all hugging face models.

    Called by src/python/web/backend/Dockerfile to pre-cache models at build time.
    """
    parser = ArgumentParser()
    parser.add_argument("--hf_access_token", dest="hf_access_token", required=True)
    args = parser.parse_args()

    initialize_models(
        hf_access_token=args.hf_access_token,
        openai_api_key=None,
        baseten_api_key=None,
        enable_heavy_models=True,
    )


if __name__ == "__main__":
    main()
