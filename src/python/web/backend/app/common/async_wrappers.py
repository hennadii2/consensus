import asyncio
from typing import Optional

from claim_pb2 import Claim
from common.db.abstract_takeaways import AbstractTakeaway, AbstractTakeaways
from common.db.hash_paper_ids import HashPaperIds
from common.db.journal_scores import JournalScores
from common.db.journal_util import get_journal_scimago_quartile, get_journal_score
from common.db.journals import Journals
from common.db.papers import Papers
from common.search.data import PaperResult
from common.search.document_types import HumanStudyKeywordEnum, StudyTypeKeywordEnum
from common.storage.connect import StorageClient
from common.storage.paper_data import read_clean_abstract
from fastapi.concurrency import run_in_threadpool
from journal_pb2 import JournalScore
from paper_pb2 import Paper
from web.backend.app.common.badges import Badges, get_badges
from web.backend.app.common.disputed import DisputedData


async def read_paper_id(
    hash_paper_ids: HashPaperIds,
    hash_paper_id: str,
) -> Optional[str]:
    return await run_in_threadpool(hash_paper_ids.read_paper_id, hash_paper_id)


async def read_hash_paper_id(
    hash_paper_ids: HashPaperIds,
    paper_id: str,
) -> Optional[str]:
    return await run_in_threadpool(hash_paper_ids.read_hash_paper_id, paper_id)


async def read_paper(
    papers: Papers,
    paper_id: str,
) -> Optional[Paper]:
    return await run_in_threadpool(papers.read_by_id, paper_id)


async def read_abstract(storage_client: StorageClient, paper: Paper) -> Optional[str]:
    return await run_in_threadpool(
        read_clean_abstract,
        storage_client,
        paper,
    )


async def read_abstract_takeaway(
    abstract_takeaways: AbstractTakeaways, paper_id: str
) -> Optional[AbstractTakeaway]:
    return await run_in_threadpool(abstract_takeaways.read_by_id, paper_id)


async def read_abstract_takeaways(
    abstract_takeaways: AbstractTakeaways, paper_ids: list[str]
) -> list[Optional[AbstractTakeaway]]:
    return await asyncio.gather(
        *[
            run_in_threadpool(
                abstract_takeaways.read_by_id,
                paper_id,
            )
            for paper_id in paper_ids
        ]
    )


async def read_journal_score(
    journals: Journals, journal_scores: JournalScores, paper: Paper
) -> Optional[JournalScore]:
    return await run_in_threadpool(
        get_journal_score,
        journals=journals,
        journal_scores=journal_scores,
        paper_metadata=paper.metadata,
    )


async def read_journal_scimago_quartile(
    journals: Journals, journal_scores: JournalScores, paper: Paper
) -> Optional[int]:
    return await run_in_threadpool(
        get_journal_scimago_quartile,
        journals=journals,
        journal_scores=journal_scores,
        paper_metadata=paper.metadata,
    )


async def read_claim_badges(
    journals: Journals,
    journal_scores: JournalScores,
    paper: Paper,
    claim: Claim,
    disputed: DisputedData,
) -> Badges:
    journal_score = await run_in_threadpool(
        get_journal_score,
        journals=journals,
        journal_scores=journal_scores,
        paper_metadata=paper.metadata,
    )

    study_type = None
    if claim.metadata.study_type:
        # Guard against unexpected values.
        # This is handled better in paper search which pre-parses on read from
        # the search index, so temp workaround in claim search for now.
        try:
            study_type = StudyTypeKeywordEnum(claim.metadata.study_type)
        except Exception:
            pass

    population_type = None
    if claim.metadata.population_type:
        # Guard against unexpected values.
        # This is handled better in paper search which pre-parses on read from
        # the search index, so temp workaround in claim search for now.
        try:
            population_type = HumanStudyKeywordEnum(claim.metadata.population_type)
        except Exception:
            pass

    badges = get_badges(
        paper_id=claim.paper_id,
        journal_score=journal_score,
        paper_metadata=paper.metadata,
        study_type=study_type,
        population_type=population_type,
        sample_size=(claim.metadata.sample_size if claim.metadata.sample_size else None),
        study_count=(claim.metadata.study_count if claim.metadata.study_count else None),
        disputed_badges=disputed.disputed_badges_by_paper_id,
        is_enhanced=claim.metadata.is_enhanced,
    )
    return badges


async def read_paper_badges(
    journals: Journals,
    journal_scores: JournalScores,
    paper: Paper,
    disputed: DisputedData,
    paper_result: PaperResult,
) -> Badges:
    journal_score = await run_in_threadpool(
        get_journal_score,
        journals=journals,
        journal_scores=journal_scores,
        paper_metadata=paper.metadata,
    )
    badges = get_badges(
        paper_id=paper.paper_id,
        journal_score=journal_score,
        paper_metadata=paper.metadata,
        study_type=paper_result.study_type,
        population_type=paper_result.population_type,
        sample_size=paper_result.sample_size,
        study_count=paper_result.study_count,
        disputed_badges=disputed.disputed_badges_by_paper_id,
        is_enhanced=False,
    )
    return badges
