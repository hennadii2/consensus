import hashlib
from dataclasses import dataclass
from typing import Optional

from common.storage.connect import StorageClient
from common.storage.disputed_results import (
    DisputedResultsJson,
    parse_data,
    read_disputed_results_text,
)
from web.backend.app.common.badges import DisputedBadge


@dataclass(frozen=True)
class DisputedData:
    version: str
    disputed_badges_by_paper_id: dict[str, DisputedBadge]
    known_background_claim_ids: dict[str, bool]


def _parse_disputed_badges(disputed: Optional[DisputedResultsJson]) -> dict[str, DisputedBadge]:
    if disputed is None:
        return {}

    disputed_badges_by_paper_id = {}
    for disputed_paper in disputed.disputed_papers:
        badge = DisputedBadge(
            reason=disputed_paper.reason,
            url=disputed_paper.url,
        )
        for paper_id in disputed_paper.paper_ids:
            disputed_badges_by_paper_id[str(paper_id)] = badge
    return disputed_badges_by_paper_id


def _parse_known_background_claim_ids(disputed: Optional[DisputedResultsJson]) -> dict[str, bool]:
    if disputed is None:
        return {}
    return dict([(claim_id, True) for claim_id in disputed.known_background_claim_ids])


def parse_disputed_data(storage_client: StorageClient) -> DisputedData:
    """
    Returns the current parsed disputed data file, which indicates papers that
    should be marked with a disputed badge.
    """
    raw_text = read_disputed_results_text(storage_client)
    version = "0"
    if raw_text is not None:
        h = hashlib.new("md5")
        h.update(raw_text.encode())
        version = h.hexdigest()
    disputed_results_json = parse_data(raw_text)
    return DisputedData(
        version=version,
        disputed_badges_by_paper_id=_parse_disputed_badges(disputed=disputed_results_json),
        known_background_claim_ids=_parse_known_background_claim_ids(
            disputed=disputed_results_json
        ),
    )
