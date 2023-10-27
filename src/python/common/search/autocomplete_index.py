import itertools
import uuid
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any, Optional

from common.search.autocomplete_queries_util import (
    make_completion_suggest,
    make_query,
    make_random_select_query,
    make_spelling_suggest,
)
from elasticsearch import Elasticsearch
from loguru import logger


@dataclass(frozen=True)
class AutocompleteIndexDocument:
    text: str


AUTOCOMPLETE_INDEX_FIELD_TEXT = "text"

AutocompleteIndexMappings: Mapping[str, Any] = {
    "properties": {
        "text": {
            "type": "search_as_you_type",
            "max_shingle_size": 4,  # max, increases index size
        },
    },
    "_source": {
        "includes": [
            AUTOCOMPLETE_INDEX_FIELD_TEXT,
        ],
    },
}

AutocompleteIndexSettings: Mapping[str, Any] = {
    "number_of_shards": 1,
    # Set to 0 to speed up ingestion. This should be increased after ingestion.
    # https://www.elastic.co/guide/en/elasticsearch/reference/master/tune-for-indexing-speed.html#_disable_replicas_for_initial_loads
    "number_of_replicas": 0,
    # Disable refresh interval to optimize for reads.
    "refresh_interval": -1,
}

UUID_NAMESPACE_QUERIES = uuid.NAMESPACE_DNS


def query_to_document_id(query: str) -> str:
    return uuid.uuid5(UUID_NAMESPACE_QUERIES, query.lower()).hex


def query_to_document(query: str) -> AutocompleteIndexDocument:
    return AutocompleteIndexDocument(text=query)


def document_to_query(doc: dict[str, Any]) -> str:
    source = {**doc["_source"]}
    return str(source[AUTOCOMPLETE_INDEX_FIELD_TEXT])


class AutocompleteIndex:
    """
    Interface class for working with the Elasticsearch AutocompleteIndex.
    """

    def __init__(self, es: Elasticsearch, index_id: str):
        self.es = es
        self.index_id = index_id

    @property
    def name(self) -> str:
        return f"autocomplete-{self.index_id}"

    @property
    def preferred(self) -> str:
        return f"{self.name}-preferred"

    @property
    def completion(self) -> str:
        return f"{self.name}-completion"

    @property
    def completion_preferred(self) -> str:
        return f"{self.completion}-preferred"

    def exists(self) -> bool:
        result = self.es.indices.exists(index=self.name)
        return result.body

    def refresh(self) -> None:
        self.es.indices.refresh(index=self.name)

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
                self.es.indices.delete(index=self.preferred)
                logger.info(f"Deleted index: {self.name}")
                logger.info(f"Deleted preferred index: {self.preferred}")
            else:
                raise ValueError(f"Failed to create index: {self.name} already exists")
        self.es.indices.create(
            index=self.name,
            settings=AutocompleteIndexSettings,
            mappings=AutocompleteIndexMappings,
        )
        self.es.indices.refresh(index=self.name)
        logger.info(f"Created index: {self.name}")

        self.es.indices.create(
            index=self.preferred,
            settings=AutocompleteIndexSettings,
            mappings=AutocompleteIndexMappings,
        )
        self.es.indices.refresh(index=self.preferred)
        logger.info(f"Created preferred index: {self.preferred}")

    def add_query(self, query: str, preferred: bool = False) -> str:
        """
        Creates an elasticsearch doc from the given query and adds it to the index.

        Raises:
            ValueError: if document with query ID already exists in index
        """

        query_id = query_to_document_id(query)
        index_name = self.preferred if preferred else self.name
        if self.es.exists(index=index_name, id=query_id):
            raise ValueError(f"Failed to add query: {query_id} already exists")

        document = query_to_document(query)
        document_dict = asdict(document)

        result = self.es.index(
            index=index_name,
            id=query_id,
            document=document_dict,
        )
        assert result["result"] == "created" and result["_id"] == query_id
        return query

    def suggest_queries(
        self,
        text: str,
        size: int = 5,
        exact_match: bool = False,
        with_spelling: bool = False,
        preferred_boost: Optional[float] = None,
        preferred_only: Optional[bool] = False,
    ) -> list[str]:
        """
        Searches for queries that are contain the given text phrase.
        """
        search_query = make_query(text=text, exact_match=exact_match)
        suggest = make_spelling_suggest(text=text) if with_spelling else None
        preferred_index_boost = 2 if preferred_boost is None else preferred_boost
        results = self.es.search(
            size=size,
            index=f"{self.preferred}" if preferred_only else f"{self.name},{self.preferred}",
            query=search_query,
            suggest=None if suggest is None else suggest.query,
            indices_boost=[{f"{self.preferred}": preferred_index_boost}],
        )

        query_suggestions = [document_to_query(hit) for hit in results["hits"]["hits"]]

        if with_spelling and suggest is not None:
            options: list[list[str]] = []

            has_spelling_suggestions = False
            for suggestion in results["suggest"][suggest.key]:
                word_options = [suggestion["text"]] + [
                    option["text"] for option in suggestion["options"] if option["score"] > 0.5
                ]
                has_spelling_suggestions = has_spelling_suggestions or len(word_options) > 1
                options.append(word_options)

            if has_spelling_suggestions:
                spelling_suggestions = [" ".join(x) for x in itertools.product(*options)]
                query_suggestions = spelling_suggestions[1:] + query_suggestions
                for suggestion in spelling_suggestions[1:]:
                    logger.info(f"adding spelling suggestion: {suggestion}")

        return query_suggestions

    def suggest_queries_completion(
        self,
        text: str,
        size: int = 5,
        preferred_only: Optional[bool] = False,
    ) -> list[str]:
        """
        Searches for queries that are contain the given text phrase.
        """
        suggest = make_completion_suggest(text=text)
        results = self.es.search(
            size=size,
            index=f"{self.completion_preferred}"
            if preferred_only
            else f"{self.completion},{self.completion_preferred}",
            suggest=suggest.query,
        )
        query_suggestions = [
            str(opt["text"]) for opt in results["suggest"][suggest.key]["options"]
        ]
        return query_suggestions

    def get_random_preferred_queries(self, size: int = 5) -> list[str]:
        """
        Returns a set of random queries.
        """
        search_query = make_random_select_query()
        results = self.es.search(
            size=size,
            index=f"{self.preferred}",
            query=search_query,
        )
        return [document_to_query(hit) for hit in results["hits"]["hits"]]
