import json
import uuid

import numpy as np
from claim_pb2 import Claim, ClaimId, ClaimNamespace
from common.models.similarity_search_embedding import (
    SimilaritySearchEmbeddingModel,
    encode_similarity_search_embedding,
)
from common.search.claim_util import generate_base_claim, generate_claim
from google.protobuf.json_format import MessageToJson, ParseDict
from paper_pb2 import Paper
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = SimilaritySearchEmbeddingModel(
    model=SentenceTransformer("all-MiniLM-L6-v2"),
    embedding_dimensions=384,
)


def mock_paper(title: str) -> Paper:
    return ParseDict(
        {
            "id": 1,
            "paper_id": "1",
            "metadata": {
                "title": title,
                "journal_name": "journal1",
                "publish_year": 1999,
                "author_names": ["Firstname A. Lastname"],
            },
        },
        Paper(),
    )


TEST_PROBABILITY = 0.5


def test_generate_claim_returns_expected_result() -> None:
    text = "Fake oranges   claim! " * 4
    paper = mock_paper("This Is a SaNITi zed? 1.23.:4-5 p--aper title?..")

    claim_id = ClaimId()
    claim_id.namespace = ClaimNamespace.EXTRACTED_FROM_PAPER
    claim_id.text = "fakeorangesclaim" * 4
    claim_id.source = "thisisasanitized12345papertitle"

    expected = Claim()
    expected.id = uuid.uuid5(uuid.NAMESPACE_DNS, json.dumps(MessageToJson(claim_id))).hex
    expected.paper_id = paper.paper_id
    expected.metadata.text = text
    expected.metadata.url_slug = ("fake-oranges-claim-" * 3) + "lastname"
    expected.metadata.probability = TEST_PROBABILITY
    expected.metadata.paper_publish_year = paper.metadata.publish_year
    expected.metadata.paper_citation_count = paper.metadata.citation_count
    expected.metadata.paper_title = paper.metadata.title
    expected.metadata.embedding[:] = encode_similarity_search_embedding(EMBEDDING_MODEL, text)
    expected.metadata.title_embedding[:] = encode_similarity_search_embedding(
        EMBEDDING_MODEL, paper.metadata.title
    )
    expected.metadata.is_enhanced = False

    actual = generate_claim(
        embedding_model=EMBEDDING_MODEL,
        namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
        display_text=text,
        original_text=text,
        probability=TEST_PROBABILITY,
        paper=paper,
        with_split_title_embedding=True,
    )
    assert actual == expected

    actual_enhanced = generate_claim(
        embedding_model=EMBEDDING_MODEL,
        namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
        display_text=text,
        original_text=text,
        probability=TEST_PROBABILITY,
        paper=paper,
        with_split_title_embedding=True,
        is_enhanced=True,
    )
    expected.metadata.is_enhanced = True
    assert actual_enhanced == expected

    actual_without_title_embedding = generate_claim(
        embedding_model=EMBEDDING_MODEL,
        namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
        display_text=text,
        original_text=text,
        probability=TEST_PROBABILITY,
        paper=paper,
        is_enhanced=True,
    )
    expected.metadata.embedding[:] = list(
        4 * np.array(expected.metadata.embedding) + np.array(expected.metadata.title_embedding)
    )
    expected.metadata.title_embedding[:] = []
    assert actual_without_title_embedding == expected


def test_generate_claim_returns_the_same_claim_id_for_same_sanitized_text() -> None:
    text1 = "Fake oranges claim."
    text2 = "Fake oranges         claim?"

    paper1 = mock_paper("This Is a SaNITi zed? 1.23.:4-5 p--aper title?..")
    paper2 = mock_paper("This Is a SaNITi zed?       1.23.:4-5 p--aper title?..?")

    actual1 = generate_claim(
        embedding_model=EMBEDDING_MODEL,
        namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
        display_text=text1,
        original_text=text1,
        probability=TEST_PROBABILITY,
        paper=paper1,
    )
    actual2 = generate_claim(
        embedding_model=EMBEDDING_MODEL,
        namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
        display_text=text2,
        original_text=text2,
        probability=TEST_PROBABILITY,
        paper=paper1,
    )
    actual3 = generate_claim(
        embedding_model=EMBEDDING_MODEL,
        namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
        display_text=text1,
        original_text=text1,
        probability=TEST_PROBABILITY,
        paper=paper2,
    )

    assert actual1.id == actual2.id
    assert actual1.id == actual3.id
    assert actual2.id == actual3.id


def test_generate_claim_returns_different_ids_for_same_claim_different_papers() -> None:
    text = "Fake oranges claim."

    paper1 = Paper()
    paper1.metadata.title = "Paper title 1"
    paper2 = Paper()
    paper2.metadata.title = "Paper title 2"

    actual1 = generate_claim(
        embedding_model=EMBEDDING_MODEL,
        namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
        display_text=text,
        original_text=text,
        probability=TEST_PROBABILITY,
        paper=paper1,
    )
    actual2 = generate_claim(
        embedding_model=EMBEDDING_MODEL,
        namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
        display_text=text,
        original_text=text,
        probability=TEST_PROBABILITY,
        paper=paper2,
    )

    assert actual1 != actual2


def test_generate_claim_returns_different_ids_for_different_claim_same_papers() -> None:
    text1 = "Fake oranges claim."
    text2 = "Fake apples claim."

    paper = mock_paper("Paper title 1")

    actual1 = generate_claim(
        embedding_model=EMBEDDING_MODEL,
        namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
        display_text=text1,
        original_text=text1,
        probability=TEST_PROBABILITY,
        paper=paper,
    )
    actual2 = generate_claim(
        embedding_model=EMBEDDING_MODEL,
        namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
        display_text=text2,
        original_text=text2,
        probability=TEST_PROBABILITY,
        paper=paper,
    )

    assert actual1 != actual2


def test_generate_claim_returns_same_ids_for_same_original_text() -> None:
    text = "Fake oranges claim."
    modified_text = "This is a fake oranges claim."

    paper = mock_paper("Paper title 1")

    actual1 = generate_claim(
        embedding_model=EMBEDDING_MODEL,
        namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
        display_text=text,
        original_text=text,
        probability=TEST_PROBABILITY,
        paper=paper,
    )
    actual2 = generate_claim(
        embedding_model=EMBEDDING_MODEL,
        namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
        display_text=modified_text,
        original_text=text,
        probability=TEST_PROBABILITY,
        paper=paper,
    )

    assert actual1.metadata.text != actual2.metadata.text
    assert actual1.id == actual2.id


def test_generate_base_claim_returns_same_claim_without_embeddings() -> None:
    text = "Fake oranges claim."
    paper = mock_paper("Paper title 1")

    actual_base_claim = generate_base_claim(
        namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
        display_text=text,
        original_text=text,
        probability=TEST_PROBABILITY,
        paper_id=paper.paper_id,
        paper_metadata=paper.metadata,
        is_enhanced=False,
    )
    assert actual_base_claim.metadata.is_enhanced is False
    assert actual_base_claim.metadata.embedding == []
    assert actual_base_claim.metadata.title_embedding == []

    actual_full_claim = generate_claim(
        embedding_model=EMBEDDING_MODEL,
        namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
        display_text=text,
        original_text=text,
        probability=TEST_PROBABILITY,
        paper=paper,
    )

    # Update unmatched fields
    actual_full_claim.metadata.embedding[:] = []
    actual_full_claim.metadata.title_embedding[:] = []
    assert actual_base_claim == actual_full_claim


def test_generate_base_claim_sets_is_enhanced() -> None:
    text = "Fake oranges claim."
    paper = mock_paper("Paper title 1")

    actual = generate_base_claim(
        namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
        display_text=text,
        original_text=text,
        probability=TEST_PROBABILITY,
        paper_id=paper.paper_id,
        paper_metadata=paper.metadata,
        is_enhanced=True,
    )
    assert actual.metadata.is_enhanced is True
