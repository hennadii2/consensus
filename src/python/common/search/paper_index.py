from typing import Any, Mapping, Optional

from elasticsearch import Elasticsearch, client
from loguru import logger
from pydantic import BaseModel, validator


class PaperIndexDocument(BaseModel):
    hash_paper_id: str
    paper_id: str
    title: Optional[str] = None
    abstract: Optional[str] = None
    publish_year: Optional[int] = None
    citation_count: Optional[int] = None
    url_slug: Optional[str] = None
    title_abstract_embedding: Optional[list[float]] = None
    sjr_best_quartile: Optional[int] = None
    study_type: Optional[str] = None
    fields_of_study: Optional[list[str]] = None
    is_biomed_plus: Optional[bool] = None
    controlled_study_type: Optional[str] = None
    population_type: Optional[str] = None
    is_rct_review: Optional[bool] = None
    sample_size: Optional[int] = None
    study_count: Optional[int] = None

    @validator("paper_id", pre=True)
    def validate_paper_id(cls, v: Any) -> str:
        if isinstance(v, int):
            return str(v)
        elif isinstance(v, str):
            return v
        raise ValueError(f"paper_id must be str or int, not {type(v)}")


PAPER_INDEX_FIELD_ABSTRACT = "abstract"


PaperIndexMappings: Mapping[str, Any] = {
    "runtime": {
        # Returns true if the paper is a controlled study, false otherwise.
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
        # Returns true if the paper is an animal study, false otherwise.
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
        # Returns true for high-quality study types, false otherwise.
        "is_quality_study_type": {
            "type": "boolean",
            "script": {
                "source": """
                String study_type = field('study_type').get('none');
                if (study_type == 'rct'
                    || study_type == 'systematic review'
                    || study_type == 'meta-analysis') {
                    emit(true);
                } else {
                    emit(false);
                }
                """
            },
        },
        # Smoothed log-transformed citation_count: Ln(citation_count + 3)
        "ln_cite_smooth": {
            "type": "double",
            "script": {
                "source": """
                int safe_cite = (int)Math.max(0, field('citation_count').get(0));
                emit(Math.log(safe_cite + 3));
                """
            },
        },
        # The age of the paper in years. Age starts at 1, as 0 is reserved for missing values.
        # TODO(cvarano): Use NOW instead of hardcoding 2023
        "paper_age": {
            "type": "long",
            "script": {
                "source": """
                int age = 2023 - field('publish_year').get(1970) + 1;
                emit((int)Math.max(1, age));
                """
            },
        },
    },
    "properties": {
        "hash_paper_id": {
            "type": "keyword",
            # Used for queries so keep indexed
        },
        "paper_id": {
            "type": "keyword",
            # Used for queries so keep indexed
        },
        # This field must be indexed as `rank_features` for the Elser Enrich Pipeline to work.
        "ml.tokens": {
            "type": "rank_features",
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
        "title": {
            "type": "text",
            "copy_to": "search_text",
            # Do not index original field, since search_text is used for queries
            "index": False,
        },
        "abstract": {
            "type": "text",
            "copy_to": "search_text",
            # Do not index original field, since search_text is used for queries
            "index": False,
        },
        "publish_year": {
            "type": "short",
            # Used for filter queries so keep indexed
        },
        "citation_count": {
            "type": "integer",
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
        "url_slug": {
            "type": "text",
            "index": False,
        },
    },
}


PaperIndexSettings: Mapping[str, Any] = {
    # Aim for 1 shard per thread; 32GB nodes have 16vCPUs
    "number_of_shards": 16,
    # Set to 0 to speed up ingestion. This should be increased after ingestion.
    # https://www.elastic.co/guide/en/elasticsearch/reference/master/tune-for-indexing-speed.html#_disable_replicas_for_initial_loads
    "number_of_replicas": 0,
    # Disable refresh interval to optimize for reads and to speed up ingestion.
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


class PaperIndex:
    """
    Interface class for working with papers indexed in Elasticsearch.
    """

    def __init__(self, es: Elasticsearch, index_name: str):
        self.es = es
        self.es_index = client.IndicesClient(self.es)
        self.index_name = index_name

    @property
    def name(self) -> str:
        return self.index_name

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
            settings=PaperIndexSettings,
            mappings=PaperIndexMappings,
        )
        self.es.indices.refresh(index=self.name)
        logger.info(f"Created index: {self.name}")

    def count(self) -> int:
        """
        Returns the number of documents in the index.
        """
        result = self.es.count(index=self.name)
        return int(result["count"])

    def paper_exists(self, paper_id: str) -> bool:
        term_query = {"term": {"paper_id": {"value": paper_id}}}
        results = self.es.search(
            size=1,
            index=self.name,
            query=term_query,
        )

        return True if len(results["hits"]["hits"]) > 0 else False

    def add_paper(self, paper: PaperIndexDocument) -> str:
        """
        Creates an elasticsearch doc from the given paper and adds it to the index.

        Raises:
            ValueError: if document with paper ID already exists in index
        """
        if self.paper_exists(paper_id=paper.paper_id):
            raise ValueError(f"Failed to add paper: {paper.paper_id} already exists")

        document_dict = {k: v for k, v in paper.dict().items() if v is not None}
        result = self.es.index(
            index=self.name,
            document=document_dict,
        )
        assert result["result"] == "created"
        return str(result["_id"])
