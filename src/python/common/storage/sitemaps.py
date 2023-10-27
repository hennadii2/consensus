from __future__ import annotations

from typing import Optional

from common.config.constants import BUCKET_NAME_PAPER_DATA
from common.storage.connect import StorageClient
from google.cloud.storage.blob import Blob  # type: ignore

# The gcs bucket path where generated sitemaps are stored.
SITEMAPS_BUCKET = f"gs://{BUCKET_NAME_PAPER_DATA}/sitemaps"


def search_index_id_without_run_timestamp(search_index_id: str) -> str:
    """
    Removes run timestamp to create a common ID for all search indexes populated
    from the same dataset.
    """
    return "-".join(search_index_id.split("-")[:-1])


def write_sitemap(
    client: StorageClient,
    search_index_id: str,
    sitemap_path: str,
    filename: str,
) -> str:
    """
    Writes a sitemap to the appropriate location in blob store and returns the URL.

    Raises:
        NotImplementedError: if environment not supported
    """

    if client.gcloud_client:
        path = f"{SITEMAPS_BUCKET}/{search_index_id}/{sitemap_path}"
        blob = Blob.from_string(path, client=client.gcloud_client)
        blob.upload_from_filename(filename)
        return path

    raise NotImplementedError("Write sitemap not supported for environment: {client.env}.")


def _read_sitemap(
    client: StorageClient,
    search_index_id: str,
    sitemap_path: str,
) -> Optional[str]:
    """
    Returns the sitemap for the given search index id and sub path.
    """

    if client.gcloud_client:
        path = f"{SITEMAPS_BUCKET}/{search_index_id}/{sitemap_path}"
        blob = Blob.from_string(path, client=client.gcloud_client)
        try:
            sitemap = blob.download_as_bytes().decode()
            return str(sitemap)
        except Exception:
            return None
    else:
        if sitemap_path == "1.xml":
            # Hard code to test a missing sitemap
            return None
        return f"<sitemap> {search_index_id} {sitemap_path} </sitemap>"


def read_sitemap(
    client: StorageClient,
    search_index_id: str,
    sitemap_path: str,
) -> Optional[str]:
    """
    Returns the sitemap for the given search index id and sub path, checks
    multiple locations for its existence.
    """
    sitemap = _read_sitemap(
        client=client,
        search_index_id=search_index_id,
        sitemap_path=sitemap_path,
    )
    if not sitemap:
        # Try again for a sitemap without the run timestamp ID
        base_id = search_index_id_without_run_timestamp(search_index_id)
        sitemap = _read_sitemap(
            client=client,
            search_index_id=base_id,
            sitemap_path=sitemap_path,
        )
    return sitemap
