from typing import Optional

import yaml
from common.config.constants import REPO_PATH_WEB_BACKEND_PROD_DEPLOYMENT
from common.storage.connect import StorageEnv, init_storage_client
from common.storage.sitemaps import read_sitemap
from loguru import logger


def main(argv=None):
    """
    Checks whether there is a deployed sitemap for the deployement search index id.
    If it does not exist, throw an exception.
    """

    storage_client = init_storage_client(StorageEnv.PROD)

    search_index_id: Optional[str] = None
    with open(REPO_PATH_WEB_BACKEND_PROD_DEPLOYMENT, "r") as stream:
        deployment = yaml.safe_load(stream)
        search_index_id = deployment["env_variables"]["WEB_BACKEND_SEARCH_INDEX"]

    if search_index_id is None:
        raise ValueError(
            f"Could not parse search index from: {REPO_PATH_WEB_BACKEND_PROD_DEPLOYMENT}"
        )

    path = "sitemap.xml"
    sitemap = read_sitemap(
        client=storage_client,
        search_index_id=search_index_id,
        sitemap_path=path,
    )
    if not sitemap:
        raise ValueError(f"Sitemap for index not found: {search_index_id}")

    logger.info(f"Found sitemap for index: {search_index_id}")


if __name__ == "__main__":
    main()
