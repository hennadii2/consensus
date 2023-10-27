import os
from typing import Optional

import pytest  # type: ignore
from claim_pb2 import Claim
from common.models.similarity_search_embedding import EMBEDDING_DIMENSIONS
from common.search.claim_index import ClaimIndex, ClaimIndexDocument, claim_to_document
from elasticsearch import Elasticsearch
from google.protobuf.json_format import ParseDict
from paper_pb2 import Paper
from testcontainers.elasticsearch import ElasticSearchContainer  # type: ignore

ES_CONFIG_FILE = "/usr/share/elasticsearch/config/{}"
ES_DATA_FILE = "src/python/common/search/resources/{}"


def mock_paper(title: str) -> Paper:
    return ParseDict(
        {
            "id": 1,
            "paper_id": "1",
            "metadata": {
                "title": title,
                "journal_name": "journal1",
                "publish_year": 1999,
                "citation_count": 10,
            },
        },
        Paper(),
    )


TEST_PAPER = mock_paper("title1")


def mock_claim(
    text: str = "claim text 1", paper: Paper = TEST_PAPER, is_enhanced: Optional[bool] = None
) -> Claim:
    claim_embedding = [0] * EMBEDDING_DIMENSIONS
    title_embedding = [0] * EMBEDDING_DIMENSIONS
    claim = ParseDict(
        {
            "id": text,
            "paper_id": paper.paper_id,
            "metadata": {
                "text": text,
                "url_slug": "tmp-slug",
                "embedding": claim_embedding,
                "title_embedding": title_embedding,
                "probability": 0.5,
                "paper_publish_year": paper.metadata.publish_year,
                "paper_citation_count": paper.metadata.citation_count,
            },
        },
        Claim(),
    )
    if is_enhanced is not None:
        claim.metadata.is_enhanced = is_enhanced
    return claim


TEST_CLAIM = mock_claim("claim text 1", TEST_PAPER)


@pytest.fixture
def claim_index():
    container = ElasticSearchContainer("elasticsearch:8.8.0")
    # mount mock stopwords file
    local_stopwords = os.path.join(os.getcwd(), ES_DATA_FILE.format("stopwords.txt"))
    es_config_stopwords = ES_CONFIG_FILE.format("stopwords.txt")
    container.with_volume_mapping(local_stopwords, es_config_stopwords)
    # mount mock synonyms file
    local_synonyms = os.path.join(os.getcwd(), ES_DATA_FILE.format("synonyms.txt"))
    es_config_synonyms = ES_CONFIG_FILE.format("synonyms.txt")
    container.with_volume_mapping(local_synonyms, es_config_synonyms)
    container.start()

    es = Elasticsearch(hosts=[container.get_url()])
    claim_index = ClaimIndex(es, "test")
    claim_index.create(delete_if_exists=True)
    try:
        yield claim_index
    finally:
        claim_index.es.close()
        container.stop()


def test_exists_succeeds_if_index_exists(claim_index) -> None:
    assert claim_index.exists()


def test_exists_succeeds_if_index_does_not_exist(claim_index) -> None:
    es = claim_index.es
    claim_index_of_unknown_index = ClaimIndex(es, "unknown")
    assert not claim_index_of_unknown_index.exists()


def test_create_succeeds(claim_index) -> None:
    name = "new_index"
    es = claim_index.es
    new_claim_index = ClaimIndex(es, name)

    assert not new_claim_index.exists()
    new_claim_index.create()
    assert new_claim_index.exists()


def test_create_succeeds_if_exists_and_delete_if_exists_true(claim_index) -> None:
    name = "new_index"
    es = claim_index.es
    new_claim_index = ClaimIndex(es, name)
    new_claim_index.create()

    assert new_claim_index.exists()
    new_claim_index.create(delete_if_exists=True)
    assert new_claim_index.exists()


def test_create_fails_if_exists_and_delete_if_exists_false(claim_index) -> None:
    name = "new_index"
    es = claim_index.es
    new_claim_index = ClaimIndex(es, name)
    new_claim_index.create()
    assert new_claim_index.exists()

    with pytest.raises(ValueError, match=f"Failed to create index: claims-{name} already exists"):
        new_claim_index.create(delete_if_exists=False)

    # Test that default is delete_if_exists=False
    with pytest.raises(ValueError, match=f"Failed to create index: claims-{name} already exists"):
        new_claim_index.create()


def test_add_claim_to_index_succeeds(claim_index) -> None:
    expected = mock_claim("claim text 1", TEST_PAPER)
    actual = claim_index.add_claim(expected)
    expected.document_id = actual.document_id
    assert actual == expected

    expected_document = {
        "claim_id": TEST_CLAIM.id,
        "text": TEST_CLAIM.metadata.text,
        "title": TEST_CLAIM.metadata.paper_title,
        "paper_id": TEST_PAPER.paper_id,
        "url_slug": TEST_CLAIM.metadata.url_slug,
        "probability": TEST_CLAIM.metadata.probability,
        "publish_year": TEST_CLAIM.metadata.paper_publish_year,
        "citation_count": TEST_CLAIM.metadata.paper_citation_count,
        "is_enhanced": False,
    }
    actual = claim_index.es.get_source(index=claim_index.name, id=actual.document_id)
    assert dict(actual) == expected_document


def test_add_claim_to_index_with_study_type_succeeds(claim_index) -> None:
    expected = mock_claim("claim text 1", TEST_PAPER)
    expected.metadata.study_type = "test_study_type"
    actual = claim_index.add_claim(expected)
    expected.document_id = actual.document_id
    assert actual == expected

    expected_document = {
        "claim_id": TEST_CLAIM.id,
        "text": TEST_CLAIM.metadata.text,
        "title": TEST_CLAIM.metadata.paper_title,
        "paper_id": TEST_PAPER.paper_id,
        "url_slug": TEST_CLAIM.metadata.url_slug,
        "probability": TEST_CLAIM.metadata.probability,
        "publish_year": TEST_CLAIM.metadata.paper_publish_year,
        "citation_count": TEST_CLAIM.metadata.paper_citation_count,
        "is_enhanced": False,
        "study_type": "test_study_type",
    }
    actual = claim_index.es.get_source(index=claim_index.name, id=actual.document_id)
    assert dict(actual) == expected_document


def test_add_claim_to_index_fails_if_already_exists(claim_index) -> None:
    claim = claim_index.add_claim(TEST_CLAIM)
    claim_index.es.indices.refresh(index=claim_index.name)

    with pytest.raises(ValueError, match=f"Failed to add claim: {claim.id} already exists"):
        claim_index.add_claim(TEST_CLAIM)


def test_claim_to_document_succeeds() -> None:
    expected = ClaimIndexDocument(
        claim_id=TEST_CLAIM.id,
        text=TEST_CLAIM.metadata.text,
        title=TEST_CLAIM.metadata.paper_title,
        paper_id=TEST_PAPER.paper_id,
        url_slug=TEST_CLAIM.metadata.url_slug,
        probability=TEST_CLAIM.metadata.probability,
        publish_year=TEST_CLAIM.metadata.paper_publish_year,
        citation_count=TEST_CLAIM.metadata.paper_citation_count,
        embedding=list(TEST_CLAIM.metadata.embedding),
        title_embedding=list(TEST_CLAIM.metadata.title_embedding),
        is_enhanced=False,
    )
    actual = claim_to_document(TEST_CLAIM, with_split_title_embedding=True)
    assert actual == expected

    expected_without_title_embedding = ClaimIndexDocument(
        claim_id=TEST_CLAIM.id,
        text=TEST_CLAIM.metadata.text,
        title=TEST_CLAIM.metadata.paper_title,
        paper_id=TEST_PAPER.paper_id,
        url_slug=TEST_CLAIM.metadata.url_slug,
        probability=TEST_CLAIM.metadata.probability,
        publish_year=TEST_CLAIM.metadata.paper_publish_year,
        citation_count=TEST_CLAIM.metadata.paper_citation_count,
        embedding=list(TEST_CLAIM.metadata.embedding),
        title_embedding=None,
        is_enhanced=False,
    )
    actual = claim_to_document(TEST_CLAIM)
    assert actual == expected_without_title_embedding


def test_claim_to_document_with_is_enhanced_succeeds() -> None:
    enhanced_test_claim = mock_claim(
        "claim text 1",
        TEST_PAPER,
        is_enhanced=True,
    )
    expected_with_enhancement = ClaimIndexDocument(
        claim_id=TEST_CLAIM.id,
        text=TEST_CLAIM.metadata.text,
        title=TEST_CLAIM.metadata.paper_title,
        paper_id=TEST_PAPER.paper_id,
        url_slug=TEST_CLAIM.metadata.url_slug,
        probability=TEST_CLAIM.metadata.probability,
        publish_year=TEST_CLAIM.metadata.paper_publish_year,
        citation_count=TEST_CLAIM.metadata.paper_citation_count,
        embedding=list(TEST_CLAIM.metadata.embedding),
        title_embedding=None,
        is_enhanced=True,
    )
    actual = claim_to_document(enhanced_test_claim)
    assert actual == expected_with_enhancement


def test_claim_to_document_allows_empty_embeddings() -> None:
    claim_no_embeddings = mock_claim()
    claim_no_embeddings.metadata.embedding[:] = []
    claim_no_embeddings.metadata.title_embedding[:] = []
    expected = ClaimIndexDocument(
        claim_id=TEST_CLAIM.id,
        text=TEST_CLAIM.metadata.text,
        title=TEST_CLAIM.metadata.paper_title,
        paper_id=TEST_PAPER.paper_id,
        url_slug=TEST_CLAIM.metadata.url_slug,
        probability=TEST_CLAIM.metadata.probability,
        publish_year=TEST_CLAIM.metadata.paper_publish_year,
        citation_count=TEST_CLAIM.metadata.paper_citation_count,
        embedding=None,
        title_embedding=None,
        is_enhanced=False,
    )
    actual = claim_to_document(
        claim_no_embeddings,
        with_split_title_embedding=True,
        allow_empty_embeddings=True,
    )
    assert actual == expected

    with pytest.raises(ValueError, match="Failed to convert claim"):
        claim_to_document(
            claim_no_embeddings,
            with_split_title_embedding=True,
            allow_empty_embeddings=False,
        )

    claim_no_title_embedding = mock_claim()
    claim_no_title_embedding.metadata.title_embedding[:] = []
    expected = ClaimIndexDocument(
        claim_id=TEST_CLAIM.id,
        text=TEST_CLAIM.metadata.text,
        title=TEST_CLAIM.metadata.paper_title,
        paper_id=TEST_PAPER.paper_id,
        url_slug=TEST_CLAIM.metadata.url_slug,
        probability=TEST_CLAIM.metadata.probability,
        publish_year=TEST_CLAIM.metadata.paper_publish_year,
        citation_count=TEST_CLAIM.metadata.paper_citation_count,
        embedding=list(TEST_CLAIM.metadata.embedding),
        title_embedding=None,
        is_enhanced=False,
    )
    with pytest.raises(ValueError, match="Failed to convert claim"):
        claim_to_document(
            claim_no_title_embedding,
            with_split_title_embedding=True,
            allow_empty_embeddings=False,
        )

    actual = claim_to_document(
        claim_no_title_embedding,
        with_split_title_embedding=False,
        allow_empty_embeddings=False,
    )
    assert actual == expected


def test_claim_to_document_adds_study_type() -> None:
    claim = mock_claim()
    claim.metadata.study_type = "test_study_type"
    expected = ClaimIndexDocument(
        claim_id=TEST_CLAIM.id,
        text=TEST_CLAIM.metadata.text,
        title=TEST_CLAIM.metadata.paper_title,
        paper_id=TEST_PAPER.paper_id,
        url_slug=TEST_CLAIM.metadata.url_slug,
        probability=TEST_CLAIM.metadata.probability,
        publish_year=TEST_CLAIM.metadata.paper_publish_year,
        citation_count=TEST_CLAIM.metadata.paper_citation_count,
        embedding=list(TEST_CLAIM.metadata.embedding),
        title_embedding=list(TEST_CLAIM.metadata.title_embedding),
        is_enhanced=False,
        study_type="test_study_type",
    )
    actual = claim_to_document(claim, with_split_title_embedding=True)
    assert actual == expected
