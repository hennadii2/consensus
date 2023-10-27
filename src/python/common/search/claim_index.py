from collections.abc import Mapping
from typing import Any, Optional

from claim_pb2 import Claim
from common.models.similarity_search_embedding import EMBEDDING_DIMENSIONS
from elasticsearch import Elasticsearch, client
from loguru import logger
from pydantic import BaseModel, validator


class ClaimIndexDocument(BaseModel):
    claim_id: str
    text: str
    title: str
    paper_id: str
    citation_count: int
    publish_year: int
    url_slug: str
    probability: float
    embedding: Optional[list[float]]
    title_embedding: Optional[list[float]]
    is_enhanced: bool
    study_type: Optional[str]
    population_type: Optional[str]
    sample_size: Optional[int]
    study_count: Optional[int]

    @validator("paper_id", pre=True)
    def validate_paper_id(cls, v: Any) -> str:
        if isinstance(v, int):
            return str(v)
        elif isinstance(v, str):
            return v
        raise ValueError(f"paper_id must be str or int, not {type(v)}")


CLAIM_INDEX_FIELD_CLAIM_ID = "claim_id"
CLAIM_INDEX_FIELD_TEXT = "text"
CLAIM_INDEX_FIELD_TITLE = "title"
CLAIM_INDEX_FIELD_PAPER_ID = "paper_id"
CLAIM_INDEX_FIELD_CITATION_COUNT = "citation_count"
CLAIM_INDEX_FIELD_PUBLISH_YEAR = "publish_year"
CLAIM_INDEX_FIELD_URL_SLUG = "url_slug"
CLAIM_INDEX_FIELD_PROBABILITY = "probability"
CLAIM_INDEX_FIELD_EMBEDDING = "embedding"
CLAIM_INDEX_FIELD_TITLE_EMBEDDING = "title_embedding"
CLAIM_INDEX_FIELD_IS_ENHANCED = "is_enhanced"
CLAIM_INDEX_FIELD_STUDY_TYPE = "study_type"

ClaimIndexMappings: Mapping[str, Any] = {
    # Exclude embeddings from _source to reduce memory footprint
    "_source": {
        "excludes": [
            CLAIM_INDEX_FIELD_EMBEDDING,
            CLAIM_INDEX_FIELD_TITLE_EMBEDDING,
        ],
    },
    "runtime": {
        "is_controlled_study": {
            "type": "boolean",
            "script": {
                "source": """
                boolean is_controlled_study = (
                    (field('controlled_study_type').get('none') == 'controlled')
                    || (field('study_type').get('none') == 'rct')
                    || (field('is_rct_review').get(false) == true)
                );
                if (is_controlled_study) {
                    emit(true);
                } else {
                    emit(false);
                }
                """
            },
        },
        "is_animal_study": {
            "type": "boolean",
            "script": {
                "source": """
                if (field('population_type').get('none') == 'animal') {
                    String study_type = field('study_type').get('none');
                    if (study_type == 'rct' || study_type == 'non-rct experimental') {
                        emit(true);
                    } else {
                        emit(false);
                    }
                } else {
                    emit(false);
                }
                """
            },
        },
    },
    "properties": {
        "claim_id": {
            "type": "keyword",
            # Used for queries so keep indexed
        },
        "paper_id": {
            "type": "keyword",
            # Used for queries so keep indexed
        },
        "search_text": {
            "type": "text",
            # Used for queries so keep indexed
            # https://www.elastic.co/guide/en/elasticsearch/reference/8.9/mixing-exact-search-with-stemming.html
            "analyzer": "english_analyzer",
            "search_analyzer": "english_search_analyzer",  # apply query-time synonyms
            "fields": {
                "exact": {
                    "type": "text",
                    "analyzer": "standard",  # for phrase matching
                    "search_analyzer": "english_synonyms_analyzer",  # for synonyms with phrase matching  # noqa: E501
                },
            },
        },
        "text": {
            "type": "text",
            "copy_to": "search_text",
            "index": False,
        },
        "title": {
            "type": "text",
            "copy_to": "search_text",
            "index": False,
        },
        "citation_count": {
            "type": "integer",
            "index": False,
        },
        "publish_year": {
            "type": "short",
            # Used for filter queries so keep indexed
        },
        "url_slug": {
            "type": "text",
            "index": False,
        },
        "probability": {
            "type": "float",
            "index": False,
        },
        "embedding": {
            "type": "dense_vector",
            "dims": EMBEDDING_DIMENSIONS,
            # Enable index and similarity if you use KNN approx search endpoint
            "index": False,
            # "similarity": "dot_product",
            # Enable `element_type: byte` when indexing quantized vectors
            # "element_type": "byte",
        },
        "title_embedding": {
            "type": "dense_vector",
            "dims": EMBEDDING_DIMENSIONS,
            # Enable index and similarity if you use KNN approx search endpoint
            "index": False,
            # "similarity": "dot_product",
            # Enable `element_type: byte` when indexing quantized vectors
            # "element_type": "byte",
        },
        "is_enhanced": {
            "type": "boolean",
            "index": False,
        },
        # See journal.proto for details on the range of values.
        "sjr_best_quartile": {
            "type": "short",
            # Used for filter queries so keep indexed
        },
        "study_type": {
            "type": "keyword",
            # Used for filter queries so keep indexed
        },
        "fields_of_study": {
            "type": "keyword",
            # Used for filter queries so keep indexed
        },
        "is_biomed_plus": {
            "type": "boolean",
            # Used for filter queries so keep indexed
        },
        # If applicable, indicates whether the paper had a "control group"
        # Applied to Biomed+ papers with study types:
        # Non-RCT Experimental, Non-RCT Observational
        "controlled_study_type": {
            "type": "keyword",
            # Used for filter queries so keep indexed
        },
        # If applicable, defines whether the study's population was human or animal
        # Applied to Biomed+ papers with study types:
        # Non-RCT Experimental, Non-RCT Observational, Case Report or RCT
        "population_type": {
            "type": "keyword",
            # Used for filter queries so keep indexed
        },
        # If applicable, true if the paper only analyzed randomized control trials
        # Applied to Biomed+ papers with study type:
        # Literature Review, Systematic Review, or Meta Analysis
        "is_rct_review": {
            "type": "boolean",
            # Used for filter queries so keep indexed
        },
        # If applicable, indicates the # of participants in a study
        # Applied to Biomed+ papers with study types:
        # Non-RCT Exp, Non-RCT Observational, Case Report or RCT
        "sample_size": {
            "type": "integer",
            # Used for filter queries so keep indexed
        },
        # If applicable, indicates the # of studies included in the review
        # Applied to Biomed+ papers with study types:
        # Literature Review, Systematic Review, or Meta Analysis
        "study_count": {
            "type": "integer",
            # Used for filter queries so keep indexed
        },
    },
}

ClaimIndexSettings: Mapping[str, Any] = {
    "number_of_shards": 3,
    # Set to 0 to speed up ingestion. This should be increased after ingestion.
    # https://www.elastic.co/guide/en/elasticsearch/reference/master/tune-for-indexing-speed.html#_disable_replicas_for_initial_loads
    "number_of_replicas": 0,
    # Disable refresh interval to optimize for reads.
    "refresh_interval": -1,
    "analysis": {
        "filter": {
            "english_stop": {
                "type": "stop",
                # this file MUST be uploaded to the cluster before indexing
                "stopwords_path": "stopwords.txt",
            },
            # if needed, we can add a keyword marker token filter to the analyzer
            # https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-keyword-marker-tokenfilter.html
            "english_stemmer": {
                "type": "stemmer",
                "language": "english",
            },
            "english_possessive_stemmer": {
                "type": "stemmer",
                "language": "possessive_english",
            },
            "english_synonyms": {
                "type": "synonym_graph",
                # this file MUST be uploaded to the cluster before indexing
                "synonyms_path": "synonyms.txt",
                # https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-reload-analyzers.html
                "updateable": True,
                "lenient": True,
            },
        },
        "analyzer": {
            "english_analyzer": {
                "tokenizer": "standard",
                "filter": [
                    "english_possessive_stemmer",
                    "lowercase",
                    "english_stop",
                    "english_stemmer",
                ],
            },
            "english_search_analyzer": {
                "tokenizer": "standard",
                "filter": [
                    "english_possessive_stemmer",
                    "lowercase",
                    "english_stop",
                    "english_stemmer",
                    "english_synonyms",
                ],
            },
            "english_synonyms_analyzer": {
                "tokenizer": "standard",
                "filter": ["lowercase", "english_synonyms"],
            },
        },
    },
}


def claim_to_document(
    claim: Claim,
    with_split_title_embedding=False,
    allow_empty_embeddings=False,
) -> ClaimIndexDocument:
    """
    Converts a claim into a ClaimIndexDocument to be added to search.
    Raises:
      ValueError: if a field value on the claim fails validations
    """
    claim_embedding = None
    skip_check = len(claim.metadata.embedding) == 0 and allow_empty_embeddings
    if not skip_check:
        claim_embedding = list(claim.metadata.embedding)
        dimens = len(claim_embedding)
        if dimens != EMBEDDING_DIMENSIONS and not skip_check:
            raise ValueError(
                "Failed to convert claim to search document: "
                + f"expected {EMBEDDING_DIMENSIONS} claim dimensions found {dimens}"
            )

    title_embedding = None
    if with_split_title_embedding:
        skip_check = len(claim.metadata.title_embedding) == 0 and allow_empty_embeddings
        if not skip_check:
            title_embedding = list(claim.metadata.title_embedding)
            dimens = len(title_embedding)
            if dimens != EMBEDDING_DIMENSIONS:
                raise ValueError(
                    "Failed to convert claim to search document: "
                    + f"expected {EMBEDDING_DIMENSIONS} title dimensions found {dimens}"
                )

    document = ClaimIndexDocument(
        claim_id=claim.id,
        text=claim.metadata.text,
        title=claim.metadata.paper_title,
        paper_id=claim.paper_id,
        url_slug=claim.metadata.url_slug,
        probability=claim.metadata.probability,
        citation_count=claim.metadata.paper_citation_count,
        publish_year=claim.metadata.paper_publish_year,
        embedding=claim_embedding,
        title_embedding=title_embedding,
        is_enhanced=claim.metadata.is_enhanced,
        study_type=(claim.metadata.study_type if claim.metadata.study_type else None),
        sample_size=(claim.metadata.sample_size if claim.metadata.sample_size else None),
        study_count=(claim.metadata.study_count if claim.metadata.study_count else None),
        population_type=(
            claim.metadata.population_type if claim.metadata.population_type else None
        ),
    )
    return document


def document_to_claim(doc_id: str, doc: dict[str, Any]) -> Claim:
    """Converts an elasticsearch document and an ID back into a Claim."""
    source = {**doc["_source"]}

    if CLAIM_INDEX_FIELD_EMBEDDING not in source:
        source[CLAIM_INDEX_FIELD_EMBEDDING] = [0] * EMBEDDING_DIMENSIONS
    if CLAIM_INDEX_FIELD_TITLE_EMBEDDING not in source:
        source[CLAIM_INDEX_FIELD_TITLE_EMBEDDING] = [0] * EMBEDDING_DIMENSIONS

    document = ClaimIndexDocument(**source)
    claim = Claim()
    claim.id = document.claim_id
    claim.document_id = doc_id
    claim.paper_id = document.paper_id
    claim.metadata.url_slug = document.url_slug
    claim.metadata.text = document.text
    claim.metadata.paper_title = document.title
    claim.metadata.probability = document.probability
    if document.embedding:
        claim.metadata.embedding[:] = document.embedding
    if document.title_embedding:
        claim.metadata.title_embedding[:] = document.title_embedding
    claim.metadata.paper_publish_year = document.publish_year
    claim.metadata.paper_citation_count = document.citation_count
    claim.metadata.is_enhanced = document.is_enhanced
    if document.study_type:
        claim.metadata.study_type = document.study_type

    if document.population_type:
        claim.metadata.population_type = document.population_type

    # Either sample size or study count will be set
    if document.sample_size:
        claim.metadata.sample_size = document.sample_size
    elif document.study_count:
        claim.metadata.study_count = document.study_count
    return claim


def claim_index_name(index_id) -> str:
    return f"claims-{index_id}"


class ClaimIndex:
    """
    Interface class for working with ClaimIndexDocuments stored in Elasticsearch.
    """

    def __init__(self, es: Elasticsearch, index_id: str):
        self.es = es
        self.es_index = client.IndicesClient(self.es)
        self.index_id = index_id

    @property
    def name(self) -> str:
        return claim_index_name(self.index_id)

    def exists(self) -> bool:
        result = self.es.indices.exists(index=self.name)
        return result.body

    def refresh(self) -> None:
        self.es_index.refresh(index=self.name)

    def create(self, delete_if_exists=False) -> None:
        """
        Creates a new elasticsearch index and fails if the index already exists and
        it has not been requested to delete.

        Raises:
            ValueError: if the index already exists
        """
        if self.exists():
            if delete_if_exists:
                self.es.indices.delete(index=self.name)
                logger.info(f"Deleted index: {self.name}")
            else:
                raise ValueError(f"Failed to create index: {self.name} already exists")
        self.es.indices.create(
            index=self.name,
            settings=ClaimIndexSettings,
            mappings=ClaimIndexMappings,
        )
        self.es.indices.refresh(index=self.name)
        logger.info(f"Created index: {self.name}")

    def count(self) -> int:
        """
        Returns the number of documents in the index.
        """
        result = self.es.count(index=self.name)
        return int(result["count"])

    def claim_exists(self, claim_id: str) -> bool:
        term_query = {"term": {"claim_id": {"value": claim_id}}}
        results = self.es.search(
            size=1,
            index=self.name,
            query=term_query,
        )

        return True if len(results["hits"]["hits"]) > 0 else False

    def add_claim(self, claim: Claim, with_split_title_embedding=False) -> Claim:
        """
        Creates an elasticsearch doc from the given claim and adds it to the index.

        Raises:
            ValueError: if document with claim ID already exists in index
        """

        if self.claim_exists(claim_id=claim.id):
            raise ValueError(f"Failed to add claim: {claim.id} already exists")

        document = claim_to_document(claim, with_split_title_embedding)
        document_dict = document.dict()
        if not with_split_title_embedding:
            document_dict.pop(CLAIM_INDEX_FIELD_TITLE_EMBEDDING)

        # Drop all None types from the dict
        document_dict = {k: v for k, v in document_dict.items() if v is not None}

        result = self.es.index(
            index=self.name,
            document=document_dict,
        )
        assert result["result"] == "created"
        claim.document_id = result["_id"]
        return claim
