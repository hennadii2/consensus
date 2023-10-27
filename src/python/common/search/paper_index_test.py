import os

import pytest  # type: ignore
from common.search.paper_index import PaperIndex, PaperIndexDocument
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


def test_exists_succeeds_if_index_exists(paper_index) -> None:
    assert paper_index.exists()


def test_exists_succeeds_if_index_does_not_exist(paper_index) -> None:
    es = paper_index.es
    paper_index_of_unknown_index = PaperIndex(es, "unknown")
    assert not paper_index_of_unknown_index.exists()


def test_create_succeeds(paper_index) -> None:
    name = "new_index"
    es = paper_index.es
    new_paper_index = PaperIndex(es, name)

    assert not new_paper_index.exists()
    new_paper_index.create()
    assert new_paper_index.exists()


def test_create_succeeds_if_exists_and_delete_if_exists_true(paper_index) -> None:
    name = "new_index"
    es = paper_index.es
    new_paper_index = PaperIndex(es, name)
    new_paper_index.create()

    assert new_paper_index.exists()
    new_paper_index.create(delete_if_exists=True)
    assert new_paper_index.exists()


def test_create_fails_if_exists_and_delete_if_exists_false(paper_index) -> None:
    name = "new_index"
    es = paper_index.es
    new_paper_index = PaperIndex(es, name)
    new_paper_index.create()
    assert new_paper_index.exists()

    with pytest.raises(ValueError, match=f"Failed to create index: {name} already exists"):
        new_paper_index.create(delete_if_exists=False)

    # Test that default is delete_if_exists=False
    with pytest.raises(ValueError, match=f"Failed to create index: {name} already exists"):
        new_paper_index.create()


def test_add_paper_to_index_succeeds(paper_index) -> None:
    expected = mock_paper()
    doc_id = paper_index.add_paper(expected)
    expected_document = {
        "hash_paper_id": TEST_PAPER.hash_paper_id,
        "paper_id": TEST_PAPER.paper_id,
        "title": TEST_PAPER.title,
        "publish_year": 2030,
        "citation_count": 100,
        "sjr_best_quartile": 2,
        "study_type": "rct",
        "is_biomed_plus": True,
        "sample_size": 5000,
    }
    actual = paper_index.es.get_source(index=paper_index.name, id=doc_id)
    assert dict(actual) == expected_document


def test_add_paper_to_index_fails_if_already_exists(paper_index) -> None:
    _ = paper_index.add_paper(TEST_PAPER)
    paper_index.es.indices.refresh(index=paper_index.name)

    with pytest.raises(
        ValueError, match=f"Failed to add paper: {TEST_PAPER.paper_id} already exists"
    ):
        paper_index.add_paper(TEST_PAPER)
