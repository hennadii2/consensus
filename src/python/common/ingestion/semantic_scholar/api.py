import argparse
import re
from dataclasses import dataclass

import requests
from common.config.secret_manager import SecretId, access_secret
from loguru import logger

S2_API_URL = "https://api.semanticscholar.org/datasets/v1/release"
S2_DOWNLOAD_PATH_REGEX = re.compile(r"(.*)\?AWSAccessKeyId=.*")


def _create_headers(token: str) -> dict:
    return {"x-api-key": f"{token}"}


def get_release_ids(token: str) -> list[str]:
    """
    Returns all release keys sorted by year.
    """
    headers = _create_headers(token)
    response = requests.get(
        S2_API_URL,
        headers=headers,
    )
    if response.status_code != 200:
        raise ValueError(response.reason)
    return list(response.json())


@dataclass(frozen=True)
class ReleaseSummary:
    release_id: str
    datasets: list[str]


def get_release_summary(token: str, release_id: str) -> ReleaseSummary:
    headers = _create_headers(token)
    response = requests.get(
        f"{S2_API_URL}/{release_id}",
        headers=headers,
    )
    if response.status_code != 200:
        raise ValueError(response.reason)
    dataset_names = []
    for dataset in response.json()["datasets"]:
        dataset_names.append(dataset["name"])
    return ReleaseSummary(
        release_id=release_id,
        datasets=dataset_names,
    )


def get_latest_release_summary(token: str) -> ReleaseSummary:
    """
    Returns a summary of the latest release.
    """
    releases = get_release_ids(token)
    latest_release = releases[-1]
    return get_release_summary(token=token, release_id=latest_release)


@dataclass(frozen=True)
class DatasetDownloadPath:
    download_path: str
    dataset: str
    release_id: str
    filename: str


def get_dataset_download_paths(
    token: str, release: ReleaseSummary, dataset: str
) -> list[DatasetDownloadPath]:
    """
    Returns S2 datasets download paths that are authed for a limited time.
    """
    if dataset not in release.datasets:
        raise ValueError(
            f"""
        Unknown dataset for release {release.release_id}: {dataset}
        Available datasets: {release.datasets}"""
        )
    headers = _create_headers(token)
    response = requests.get(
        f"{S2_API_URL}/{release.release_id}/dataset/{dataset}",
        headers=headers,
    )
    if response.status_code != 200:
        raise ValueError(response.reason)
    data = response.json()
    if "files" not in data:
        raise ValueError("Dataset response missing expected field: files")

    dataset_download_paths = []
    for s2_path in data["files"]:
        s2_path_match = S2_DOWNLOAD_PATH_REGEX.search(s2_path)
        if s2_path_match is None:
            raise ValueError(f"{s2_path} did not match regex {S2_DOWNLOAD_PATH_REGEX}")
        s2_filename = s2_path_match.group(1).split("/")[-1]
        dataset_download_paths.append(
            DatasetDownloadPath(
                download_path=s2_path,
                dataset=dataset,
                release_id=release.release_id,
                filename=s2_filename,
            )
        )
    return dataset_download_paths


def main(argv=None):
    """
    Calls the S2 API.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--s2_token",
        dest="s2_token",
        help="S2 API token.",
    )
    parser.add_argument(
        "--list_releases",
        action="store_true",
        help="If set, lists releases",
    )
    parser.add_argument(
        "--latest_release",
        action="store_true",
        help="If set, returns latest release",
    )
    parser.add_argument(
        "--latest_download_paths_for_dataset",
        dest="latest_download_paths_for_dataset",
        help="If set, returns latest release download paths",
    )
    args, _ = parser.parse_known_args(argv)

    handled = False

    if args.s2_token is None:
        args.s2_token = access_secret(SecretId.S2_API_KEY)

    if args.list_releases:
        releases = get_release_ids(args.s2_token)
        logger.info(releases)
        handled = True

    if args.latest_release:
        release = get_latest_release_summary(args.s2_token)
        logger.info(release)
        handled = True

    if args.latest_download_paths_for_dataset:
        release = get_latest_release_summary(args.s2_token)
        dataset = args.latest_download_paths_for_dataset
        download_paths = get_dataset_download_paths(args.s2_token, release, dataset)
        logger.info(download_paths)
        handled = True

    if not handled:
        logger.error("You must set at least one action argument, see parser options.")
        return


if __name__ == "__main__":
    main()
