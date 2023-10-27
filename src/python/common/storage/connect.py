from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import google.cloud.storage as storage  # type: ignore


class StorageEnv(Enum):
    """
    All supported storage environments.
    """

    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


@dataclass(frozen=True)
class StorageClient:
    env: StorageEnv
    gcloud_client: Optional[storage.Client]


def init_storage_client(env: StorageEnv) -> StorageClient:
    return StorageClient(
        env=env,
        gcloud_client=None if env == StorageEnv.LOCAL else storage.Client(),
    )
