import uuid
from enum import Enum
from string import punctuation
from typing import Any, List, Mapping, Optional

import nltk
from common.search.data import PaperResult
from common.search.paper_index import PAPER_INDEX_FIELD_ABSTRACT, PaperIndexDocument
from paper_metadata_pb2 import PaperMetadata

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("averaged_perceptron_tagger")

stop_words = list(set(nltk.corpus.stopwords.words("english")))

# =============================================================================
# START WARNING ===============================================================
# =============================================================================
# These values should not be changed unless you are intentionally invalidating
# all existing hash_paper_id values. Please be careful!
# =============================================================================

PAPER_ID_NAMESPACE = uuid.UUID("6e5c702c-c854-4c05-92fd-50335ffcceea")
PAPER_ID_OBFUSCATION_SALT = "8r0CV^R+1g]sN@K+"


class PaperIdProvider(Enum):
    # You can safely add providers, but do not change the assigned enum strings
    S2 = "S2"


# =============================================================================
# END WARNING =================================================================
# =============================================================================


def generate_hash_paper_id(provider: PaperIdProvider, provider_id: str) -> str:
    """
    Generates an obfuscated ID for a paper given its provider's id.

    Raises:
        ValueError: if an S2 ID does not have its expected prefix
        See https://consensus-app.atlassian.net/l/cp/re4Qfp1b for details
    """
    if provider == PaperIdProvider.S2:
        if not provider_id.startswith(f"{provider.value}:"):
            raise ValueError(
                f"Failed to generate hash paper id: S2 id does not start with S2 prefix: {provider_id}"  # noqa: E501
            )
        return uuid.uuid5(PAPER_ID_NAMESPACE, f"{PAPER_ID_OBFUSCATION_SALT}:{provider_id}").hex
    raise NotImplementedError(
        f"Failed to generate hash paper id: unknown provider: {provider.value}"  # noqa: E501
    )


def document_to_paper(doc: Mapping[str, Any]) -> PaperResult:
    """Converts an elasticsearch json document into a PaperResult."""
    source = {**doc["_source"]}
    paper = PaperResult(**source)
    paper.doc_id = doc["_id"]
    if PAPER_INDEX_FIELD_ABSTRACT in doc["_source"]:
        paper.display_text = doc["_source"][PAPER_INDEX_FIELD_ABSTRACT]
    paper.debug_explanation = doc.get("_explanation", None)
    return paper


def _generate_url_slug(paper_metadata: PaperMetadata, character_limit=50) -> str:
    """
    Generates a short hyphenated string to represent a paper as a slug url.

    To shorten the title and generate the slug this function:
      - Removes stop words and adjectives
      - Removes all words past a character limit
      - Appends the 1st author's last name to the end of the slug

    Raises:
        ValueError: if generated url slug text is empty
    """
    # Remove punctuation
    title_no_punct = "".join([c for c in paper_metadata.title if c not in punctuation])

    # Remove stop words and tokens that have length <= 3
    tokens = nltk.tokenize.word_tokenize(title_no_punct)
    tokens = [x for x in tokens if x not in stop_words if len(x) > 3]

    # Filter adjectives based on their part of speech tags
    words = [x[0] for x in nltk.pos_tag(tokens) if not x[1].startswith("J")]

    if not len(words):
        raise ValueError(
            f"Failed to generate url slug: all words removed for: {paper_metadata.title}"
        )

    # Force remaining words to under 50 characters
    slug_length = 0
    summary = []
    for word in words:
        slug_length = slug_length + len(word)
        if slug_length > character_limit:
            break
        summary.append(word)
    summary = summary if len(summary) else [words[0]]

    # Add author to slug if available
    primary_author_lastname: list[str] = []
    if len(paper_metadata.author_names):
        fullname = paper_metadata.author_names[0]
        fullname = "".join([c for c in fullname if c not in punctuation])
        primary_author_lastname = [fullname.split()[-1]]

    return "-".join([*summary, *primary_author_lastname]).lower()


def generate_url_slug(paper_metadata: PaperMetadata) -> str:
    return _generate_url_slug(paper_metadata)


def generate_paper(
    hash_paper_id: str,
    paper_id: str,
    abstract: str,
    paper_metadata: PaperMetadata,
    title_abstract_embedding: List[float],
    sjr_best_quartile: Optional[int],
    study_type: Optional[str],
) -> PaperIndexDocument:
    paper = PaperIndexDocument(
        hash_paper_id=hash_paper_id,
        paper_id=paper_id,
        abstract=abstract,
        title=paper_metadata.title,
        publish_year=paper_metadata.publish_year,
        citation_count=paper_metadata.citation_count,
        url_slug=_generate_url_slug(paper_metadata),
        title_abstract_embedding=title_abstract_embedding,
        sjr_best_quartile=sjr_best_quartile,
        study_type=study_type,
    )

    return paper
