from typing import Optional

from common.db.journal_scores import JournalScores
from common.db.journals import Journals
from journal_pb2 import JournalScore
from paper_metadata_pb2 import PaperMetadata


def _get_journal_score_by_issn_with_name_fallback(
    journals: Journals, journal_scores: JournalScores, paper_metadata: PaperMetadata
) -> Optional[JournalScore]:
    """
    Returns a journal score for the paper if possible.
    """
    journal_issns = [paper_metadata.journal_issn] + list(paper_metadata.journal_alternate_issns)
    journal = journals.read_by_issn_with_name_fallback(
        issn_list=journal_issns,
        name=paper_metadata.journal_name,
    )
    if not journal or not journal:
        return None

    return journal_scores.get_computed_score(
        journal_id=journal.id,
        year=paper_metadata.publish_year,
    )


def _get_journal_scimago_quartile_by_issn_with_name_fallback(
    journals: Journals, journal_scores: JournalScores, paper_metadata: PaperMetadata
) -> Optional[int]:
    """
    Returns a journal SJR quartile for the paper if possible.
    """
    journal_issns = [paper_metadata.journal_issn] + list(paper_metadata.journal_alternate_issns)
    journal = journals.read_by_issn_with_name_fallback(
        issn_list=journal_issns,
        name=paper_metadata.journal_name,
    )
    if not journal or not journal:
        return None

    return journal_scores.get_latest_scimago_quartile(
        journal_id=journal.id,
    )


def _get_journal_score_by_name(
    journals: Journals, journal_scores: JournalScores, paper_metadata: PaperMetadata
) -> Optional[JournalScore]:
    """
    Returns a journal score for the paper if possible.
    """
    journal_id = paper_metadata.journal_id
    if not journal_id:
        # Lookup the journal by name if an ID was not stored on the paper
        journal = journals.read_by_name(paper_metadata.journal_name)
        if journal:
            journal_id = journal.id

    if journal_id:
        # Lookup the journal score if a journal was found for the paper
        return journal_scores.get_computed_score(
            journal_id=journal_id,
            year=paper_metadata.publish_year,
        )
    else:
        return None


def _get_journal_scimago_quartile_by_name(
    journals: Journals, journal_scores: JournalScores, paper_metadata: PaperMetadata
) -> Optional[int]:
    journal_id = paper_metadata.journal_id
    if not journal_id:
        # Lookup the journal by name if an ID was not stored on the paper
        journal = journals.read_by_name(paper_metadata.journal_name)
        if journal:
            journal_id = journal.id

    if journal_id:
        # Lookup the journal score if a journal was found for the paper
        return journal_scores.get_latest_scimago_quartile(
            journal_id=journal_id,
        )
    else:
        return None


def get_journal_score(
    journals: Journals,
    journal_scores: JournalScores,
    paper_metadata: PaperMetadata,
    use_issn=False,
) -> Optional[JournalScore]:
    """
    Returns a journal score for the paper if possible.
    """
    if use_issn:
        return _get_journal_score_by_issn_with_name_fallback(
            journals=journals,
            journal_scores=journal_scores,
            paper_metadata=paper_metadata,
        )
    else:
        return _get_journal_score_by_name(
            journals=journals,
            journal_scores=journal_scores,
            paper_metadata=paper_metadata,
        )


def get_journal_scimago_quartile(
    journals: Journals,
    journal_scores: JournalScores,
    paper_metadata: PaperMetadata,
    use_issn=False,
) -> Optional[int]:
    """
    Returns a journal SJR quartile for the paper if possible.
    """
    if use_issn:
        return _get_journal_scimago_quartile_by_issn_with_name_fallback(
            journals=journals,
            journal_scores=journal_scores,
            paper_metadata=paper_metadata,
        )
    else:
        return _get_journal_scimago_quartile_by_name(
            journals=journals,
            journal_scores=journal_scores,
            paper_metadata=paper_metadata,
        )
