"""
TODO(cvarano): pytest does not natively support async tests; look into pytest-asyncio
"""
import os
from typing import Optional

import pytest  # type: ignore
from claim_pb2 import Claim
from common.models.similarity_search_embedding import EMBEDDING_DIMENSIONS
from common.search.async_claim_index import AsyncClaimIndex
from common.search.claim_index import ClaimIndex
from elasticsearch import AsyncElasticsearch, Elasticsearch
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
def async_claim_index():
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
    es.close()

    async_es = AsyncElasticsearch(hosts=[container.get_url()])
    async_claim_index = AsyncClaimIndex(async_es, "test")
    try:
        yield async_claim_index
    finally:
        async_claim_index.es.close()
        container.stop()


async def test_get_by_claim_id_returns_none_if_claim_does_not_exist(async_claim_index) -> None:
    actual = await async_claim_index.get_claim_by_id("unknown")
    assert actual is None


async def test_get_by_claim_id_succeeds(async_claim_index) -> None:
    claim1 = mock_claim("Fake oranges claim.", TEST_PAPER)
    claim2 = mock_claim("Fake apples claim.", TEST_PAPER)
    async_claim_index.add_claim(claim1)
    async_claim_index.add_claim(claim2)
    async_claim_index.es.indices.refresh(index=async_claim_index.name)

    assert claim1 != claim2

    actual = await async_claim_index.get_claim_by_id(claim_id=claim1.id)
    assert actual == claim1

    actual = await async_claim_index.get_claim_by_id(claim_id=claim2.id)
    assert actual == claim2


async def test_get_by_claim_ids_succeeds(async_claim_index) -> None:
    claim1 = mock_claim("Fake oranges claim.", TEST_PAPER)
    claim2 = mock_claim("Fake apples claim.", TEST_PAPER)
    async_claim_index.add_claim(claim1)
    async_claim_index.add_claim(claim2)
    async_claim_index.es.indices.refresh(index=async_claim_index.name)

    actual = await async_claim_index.get_claims_by_id(claim_ids=[])
    assert actual == []

    actual = await async_claim_index.get_claims_by_id(claim_ids=[claim1.id])
    assert actual == {f"{claim1.id}": claim1}

    actual = await async_claim_index.get_claims_by_id(claim_ids=[claim2.id])
    assert actual == {f"{claim2.id}": claim2}

    actual = await async_claim_index.get_claims_by_id(claim_ids=[claim1.id, claim2.id])
    assert actual == {f"{claim1.id}": claim1, f"{claim2.id}": claim2}
