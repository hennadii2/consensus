from typing import Optional

from common.search.document_types import HumanStudyKeywordEnum, StudyTypeKeywordEnum
from pydantic import BaseModel


class PaperResult(BaseModel):
    hash_paper_id: str
    paper_id: str
    # The auto-generated Elasticsearch document id
    doc_id: Optional[str] = None
    title: Optional[str] = None
    # The text to display in the search results, e.g. the extracted answer, or the abstract summary
    display_text: Optional[str] = None
    url_slug: Optional[str] = None
    study_type: Optional[StudyTypeKeywordEnum] = None
    population_type: Optional[HumanStudyKeywordEnum] = None
    sample_size: Optional[int] = None
    study_count: Optional[int] = None
    # For debugging only
    debug_explanation: Optional[dict] = None
