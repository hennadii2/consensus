import os
import uuid

import pytest  # type: ignore
from common.search.data import PaperResult
from common.search.paper_index import PaperIndex, PaperIndexDocument
from common.search.paper_util import (
    PAPER_ID_NAMESPACE,
    PAPER_ID_OBFUSCATION_SALT,
    PaperIdProvider,
    document_to_paper,
    generate_hash_paper_id,
)
from elasticsearch import Elasticsearch
from testcontainers.elasticsearch import ElasticSearchContainer  # type: ignore

ES_CONFIG_FILE = "/usr/share/elasticsearch/config/{}"
ES_DATA_FILE = "src/python/common/search/resources/{}"


def mock_paper(
    title: str = "paper title 1",
) -> PaperIndexDocument:
    return PaperIndexDocument(
        hash_paper_id="hash_paper_id_1",
        paper_id="paper_id_1",
        title=title,
        abstract="mock_abstract",
        publish_year=2030,
        citation_count=100,
        sjr_best_quartile=2,
        study_type="rct",
        is_biomed_plus=True,
        sample_size=5000,
    )


TEST_PAPER = mock_paper()


@pytest.fixture
def paper_index():
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
    paper_index = PaperIndex(es, "test")
    paper_index.create(delete_if_exists=True)
    try:
        yield paper_index
    finally:
        paper_index.es.close()
        container.stop()


def test_document_to_paper_succeeds(paper_index) -> None:
    doc_id = paper_index.add_paper(TEST_PAPER)
    expected = PaperResult(
        hash_paper_id=TEST_PAPER.hash_paper_id,
        paper_id=TEST_PAPER.paper_id,
        doc_id=doc_id,
        title=TEST_PAPER.title,
        display_text=TEST_PAPER.abstract,
        url_slug=None,
        study_type=TEST_PAPER.study_type,
        population_type=None,
        sample_size=5000,
        study_count=None,
        debug_explanation=None,
    )

    result = paper_index.es.get(index=paper_index.name, id=doc_id)
    actual = document_to_paper(result)
    assert actual == expected


def test_document_to_paper_without_abstract_succeeds(paper_index) -> None:
    paper_with_abstract_removed = mock_paper()
    paper_with_abstract_removed.abstract = None
    doc_id = paper_index.add_paper(paper_with_abstract_removed)
    expected = PaperResult(
        hash_paper_id=TEST_PAPER.hash_paper_id,
        paper_id=TEST_PAPER.paper_id,
        doc_id=doc_id,
        title=TEST_PAPER.title,
        display_text=None,
        url_slug=None,
        study_type=TEST_PAPER.study_type,
        population_type=None,
        sample_size=5000,
        study_count=None,
        debug_explanation=None,
    )

    result = paper_index.es.get(index=paper_index.name, id=doc_id)
    actual = document_to_paper(result)
    assert actual == expected


def test_generate_hash_paper_id_succeeds() -> None:
    s2_id = "S2:55818421"
    actual = generate_hash_paper_id(PaperIdProvider.S2, s2_id)
    expected = uuid.uuid5(
        PAPER_ID_NAMESPACE,
        f"{PAPER_ID_OBFUSCATION_SALT}:{s2_id}",
    ).hex
    assert actual == expected
    assert actual == "0b0b94c6aa485024b90414e16dcd64a1"

    s2_id = "S2:685818421"
    expected = uuid.uuid5(
        PAPER_ID_NAMESPACE,
        f"{PAPER_ID_OBFUSCATION_SALT}:{s2_id}",
    ).hex
    actual = generate_hash_paper_id(PaperIdProvider.S2, s2_id)
    assert actual == expected
    assert actual == "46d7193059f35a08b4c541032402f0f3"


def test_generate_hash_paper_id_fails_if_s2_id_is_malformed() -> None:
    s2_id_no_prefix = "55818421"
    expected = uuid.uuid5(
        PAPER_ID_NAMESPACE,
        f"{PAPER_ID_OBFUSCATION_SALT}:S2:{s2_id_no_prefix}",
    ).hex
    actual = generate_hash_paper_id(PaperIdProvider.S2, f"S2:{s2_id_no_prefix}")
    assert actual == expected

    with pytest.raises(
        ValueError,
        match=f"Failed to generate hash paper id: S2 id does not start with S2 prefix: {s2_id_no_prefix}",  # noqa: E501
    ):
        generate_hash_paper_id(PaperIdProvider.S2, s2_id_no_prefix)
