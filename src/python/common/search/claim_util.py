from __future__ import annotations

import json
import re
import uuid
from string import punctuation

import nltk
import numpy as np
from claim_pb2 import Claim, ClaimId, ClaimMetadata, ClaimNamespace
from common.models.similarity_search_embedding import (
    SimilaritySearchEmbeddingModel,
    encode_similarity_search_embedding,
)
from google.protobuf.json_format import MessageToJson
from paper_metadata_pb2 import PaperMetadata
from paper_pb2 import Paper

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("averaged_perceptron_tagger")

stop_words = list(set(nltk.corpus.stopwords.words("english")))

BOOST_WEIGHTING_CLAIM_EMBEDDING = 4
BOOST_WEIGHTING_TITLE_EMBEDDING = 1


def _generate_url_slug(text: str, paper_metadata: PaperMetadata, character_limit=50) -> str:
    """
    Generates a short hyphenated string to represent a claim as a slug url.

    To shorten the text and generate the slug this function:
      - Removes stop words and adjectives
      - Removes all words past a character limit
      - Appends the 1st author's last name to the end of the slug

    Raises:
        ValueError: if generated url slug text is empty
    """
    # Remove punctuation
    text_no_punct = "".join([c for c in text if c not in punctuation])

    # Remove stop words and tokens that have length <= 3
    tokens = nltk.tokenize.word_tokenize(text_no_punct)
    tokens = [x for x in tokens if x not in stop_words if len(x) > 3]

    # Filter adjectives based on their part of speech tags
    words = [x[0] for x in nltk.pos_tag(tokens) if not x[1].startswith("J")]

    if not len(words):
        raise ValueError(f"Failed to generate url slug: all words removed for: {text}")

    # Force remaining words to under 50 chatacters
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


def _sanitize_text_for_stable_id(text: str) -> str:
    """
    Strips text down to a basic set of characters to reduce chance of changing
    a stable ID due to edits introduced by simple formatting or text cleaning.
    """
    sanitized = re.sub(r"[\W_]+", "", text).lower()
    if len(sanitized) <= 0:
        raise ValueError(
            "Failed to sanitize text for stable ID: field is too short: "
            + f"'{text}' sanitized to '{sanitized}'"
        )
    return sanitized


def generate_stable_claim_id(
    namespace: ClaimNamespace.V, original_claim_text: str, paper_title: str
) -> str:
    """
    Returns a stable claim ID for a namespace, claim, and paper title.

    Raises:
        NotImplementedError: if namespace is not yet supported
    """
    UUID_NAMESPACE = uuid.NAMESPACE_DNS
    if namespace == ClaimNamespace.EXTRACTED_FROM_PAPER:
        claim_id = ClaimId()
        claim_id.namespace = namespace
        claim_id.text = _sanitize_text_for_stable_id(text=original_claim_text)
        claim_id.source = _sanitize_text_for_stable_id(text=paper_title)
        return uuid.uuid5(UUID_NAMESPACE, json.dumps(MessageToJson(claim_id))).hex
    else:
        raise NotImplementedError(
            f"Failed to generate claim id: unsupported namespace {namespace}"
        )


def _generate_claim(
    namespace: ClaimNamespace.V,
    display_text: str,
    original_text: str,
    probability: float,
    paper_id: str,
    paper_metadata: PaperMetadata,
    is_enhanced: bool,
) -> Claim:
    """
    Creates a claim with a stable ID for the given paper and sentence text.

    Claim text and paper title is sanitized to try to keep a stable ID across small
    changes introduced by cleaning or raw text versions.

    Raises:
        NotImplementedError: if namespace is not yet supported
    """

    stable_claim_id = generate_stable_claim_id(
        namespace=namespace,
        original_claim_text=original_text,
        paper_title=paper_metadata.title,
    )

    metadata = ClaimMetadata()
    metadata.text = display_text
    metadata.url_slug = _generate_url_slug(
        text=display_text,
        paper_metadata=paper_metadata,
    )
    metadata.probability = probability
    metadata.paper_publish_year = paper_metadata.publish_year
    metadata.paper_citation_count = paper_metadata.citation_count
    metadata.paper_title = paper_metadata.title
    metadata.is_enhanced = is_enhanced

    claim = Claim()
    claim.id = stable_claim_id
    claim.paper_id = paper_id
    claim.metadata.CopyFrom(metadata)

    return claim


def generate_claim(
    embedding_model: SimilaritySearchEmbeddingModel,
    namespace: ClaimNamespace.V,
    display_text: str,
    original_text: str,
    probability: float,
    paper: Paper,
    with_split_title_embedding=False,
    is_enhanced=False,
) -> Claim:
    """
    Creates a claim with a stable ID for the given paper and sentence text.

    Claim text and paper title is sanitized to try to keep a stable ID across small
    changes introduced by cleaning or raw text versions.

    Raises:
        NotImplementedError: if namespace is not yet supported
    """
    claim = _generate_claim(
        namespace=namespace,
        display_text=display_text,
        original_text=original_text,
        probability=probability,
        paper_metadata=paper.metadata,
        paper_id=paper.paper_id,
        is_enhanced=is_enhanced,
    )
    claim_embedding = encode_similarity_search_embedding(embedding_model, display_text)
    title_embedding = encode_similarity_search_embedding(embedding_model, paper.metadata.title)

    if with_split_title_embedding:
        # Use separate embedding vectors for testing
        claim.metadata.embedding[:] = claim_embedding
        claim.metadata.title_embedding[:] = title_embedding
    else:
        # Otherwise, combine the claim and title embeddings into a single vector
        a: np.ndarray = BOOST_WEIGHTING_CLAIM_EMBEDDING * np.array(claim_embedding)
        b: np.ndarray = BOOST_WEIGHTING_TITLE_EMBEDDING * np.array(title_embedding)
        claim.metadata.embedding[:] = list(a + b)

    return claim


def generate_base_claim(
    namespace: ClaimNamespace.V,
    display_text: str,
    original_text: str,
    probability: float,
    paper_id: str,
    paper_metadata: PaperMetadata,
    is_enhanced: bool,
) -> Claim:
    """
    Creates a base claim that does not yet have embeddings.

    Raises:
        NotImplementedError: if namespace is not yet supported
    """

    return _generate_claim(
        namespace=namespace,
        display_text=display_text,
        original_text=original_text,
        probability=probability,
        paper_id=paper_id,
        paper_metadata=paper_metadata,
        is_enhanced=is_enhanced,
    )
