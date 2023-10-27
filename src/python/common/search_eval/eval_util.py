import os
from typing import Any, List, Optional, Tuple

import pandas as pd
from common.models.similarity_search_embedding import (
    SimilaritySearchEmbeddingModel,
    encode_similarity_search_embedding,
)
from common.search.claim_index import ClaimIndex
from common.search.paper_index import PaperIndex
from common.search.queries_util import (
    make_keyword_search_query,
    make_paper_keyword_search_query,
    make_paper_similarity_search_rescore_query,
    make_paper_sort_rescore_query,
    make_similarity_search_rescore_query,
    make_sort_rescore_query,
)
from common.search.search_util import (
    DEFAULT_SEARCH_CONFIG,
    RankingParams,
    SearchFilter,
    SortParams,
    quantize_vector,
)
from common.search_eval.constants import (
    QUERY_COL,
    RANK_COL,
    RELEVANCE_FEATURES,
    SEARCH_TESTING_QUERY_LIST,
)
from common.storage.connect import StorageClient
from common.storage.gcs_util import (
    SEARCH_EVAL_ANNOTATIONS_OUTPUT_PREFIX,
    SEARCH_EVAL_BUCKET,
    SEARCH_EVAL_CENTAUR_LABELS_PATH,
    SEARCH_EVAL_CENTAUR_UPLOAD_PATH,
    SEARCH_EVAL_TO_ANNOTATE_PREFIX,
)
from google.cloud import storage
from loguru import logger
from pydantic import BaseModel
from web.backend.app.common.disputed import parse_disputed_data
from web.backend.app.endpoints.search.search_util import TextCleaningOptions, TextType, _clean_text

NANOS_TO_MILLIS = 1e6


class RelevanceDocument(BaseModel):
    doc_id: str
    paper_id: Optional[str] = None
    claim_id: Optional[str] = None
    title: Optional[str] = None
    text: Optional[str] = None
    score: Optional[float] = None
    citation_count: Optional[int] = None
    probability: Optional[float] = None
    publish_year: Optional[int] = None
    sjr_best_quartile: Optional[int] = None
    doi: Optional[str] = None


# Experimental queries


def _make_aknn_query(query_vector: list[Any], k: int, num_candidates: int) -> dict[str, Any]:
    return {
        "field": "embedding",
        "query_vector": query_vector,
        "k": k,
        "num_candidates": num_candidates,
    }


def _make_aknn_multifield_query(
    query_vector: list[Any], k: int, num_candidates: int
) -> list[dict[str, Any]]:
    return [
        {
            "field": "embedding",
            "query_vector": query_vector,
            "k": k,
            "num_candidates": num_candidates,
        },
        {
            "field": "title_embedding",
            "query_vector": query_vector,
            "k": k,
            "num_candidates": num_candidates,
        },
    ]


def _make_elser_query(
    text_query: str,
) -> dict[str, Any]:
    elser_query = {
        "text_expansion": {
            "ml.tokens": {
                "model_id": ".elser_model_1",
                "model_text": text_query,
            }
        }
    }

    return elser_query


# End experimental queries


def parse_results_from_es_response(response: Any) -> List[RelevanceDocument]:
    documents = [
        RelevanceDocument(
            doc_id=doc["_id"],
            paper_id=doc["fields"]["paper_id"][0],
            claim_id=doc["fields"]["claim_id"][0],
            title=doc["fields"]["title"][0],
            text=doc["fields"]["text"][0],
            score=doc["_score"],
            citation_count=doc["fields"]["citation_count"][0],
            probability=doc["fields"]["probability"][0],
            publish_year=doc["fields"]["publish_year"][0],
            sjr_best_quartile=(
                float(doc["fields"]["sjr_best_quartile"][0])
                if "sjr_best_quartile" in doc["fields"]
                else None
            ),
        )
        for doc in response["hits"]["hits"]
    ]
    return documents


def parse_paper_results_from_es_response(response: Any) -> List[RelevanceDocument]:
    documents = [
        RelevanceDocument(
            doc_id=doc["_id"],
            paper_id=doc["fields"]["paper_id"][0],
            title=doc["fields"]["title"][0],
            text=doc["fields"]["abstract"][0],
            score=doc["_score"],
            citation_count=doc["fields"]["citation_count"][0],
            publish_year=doc["fields"]["publish_year"][0],
            sjr_best_quartile=(
                float(doc["fields"]["sjr_best_quartile"][0])
                if "sjr_best_quartile" in doc["fields"]
                else None
            ),
        )
        for doc in response["hits"]["hits"]
    ]
    return documents


def execute_elasticsearch_query(
    claim_index: ClaimIndex,
    text_query: str,
    query_vector: List[Any],
    size: int,
    search_filter: Optional[SearchFilter] = None,
    sort_params: Optional[SortParams] = None,
    knn_params: Optional[dict] = None,
    use_vector_sim: bool = True,
    use_rescore: bool = True,
) -> Any:
    # Construct elasticsearch query
    keyword_query = make_keyword_search_query(
        text_query,
        search_filter=search_filter if search_filter else DEFAULT_SEARCH_CONFIG.search_filter,
    )
    sort_params = sort_params if sort_params else DEFAULT_SEARCH_CONFIG.metadata_sort_params
    rescore = []
    boost_params = DEFAULT_SEARCH_CONFIG.vector_search_boost_params
    if use_vector_sim:
        rescore.append(
            make_similarity_search_rescore_query(
                query_embedding=query_vector,
                window_size=DEFAULT_SEARCH_CONFIG.vector_search_window_size,
                similarity_weight=sort_params.similarity_weight,
                claim_embedding_boost=(
                    None if boost_params is None else boost_params.claim_embedding_boost
                ),
                title_embedding_boost=(
                    None if boost_params is None else boost_params.title_embedding_boost
                ),
            )
        )
    if use_rescore:
        rescore.append(
            make_sort_rescore_query(
                window_size=sort_params.window_size,
                probability_weight=sort_params.probability_weight,
                citation_count_weight=sort_params.citation_count_weight,
                citation_count_min=sort_params.citation_count_min,
                citation_count_max=sort_params.citation_count_max,
                publish_year_weight=sort_params.publish_year_weight,
                publish_year_min=sort_params.publish_year_min,
                publish_year_max=sort_params.publish_year_max,
                best_quartile_weight=sort_params.best_quartile_weight,
                best_quartile_default=sort_params.best_quartile_default,
            )
        )

    # TODO(cvarano): separate out experimental queries for easier tracking
    track_total_hits = None  # Set to True for ELSER query
    # Enable this for ELSER query
    # keyword_query = _make_elser_query(text_query)

    knn_query = None
    # Enable this for approximate knn search
    # if knn_params is not None:
    #     knn_query = _make_aknn_query(query_vector, knn_params["k"], knn_params["num_candidates"])

    request_fields = ["text", "title", "claim_id", "paper_id", "probability"] + RELEVANCE_FEATURES
    response = claim_index.es.search(
        index=claim_index.name,
        size=size,
        query=keyword_query,
        knn=knn_query,
        rescore=rescore if rescore else None,
        rank=knn_params.get("rank", None) if knn_params is not None else None,
        source=False,
        fields=request_fields,  # type: ignore [arg-type]
        track_total_hits=track_total_hits,
    )
    return response


def execute_elasticsearch_paper_query(
    paper_index: PaperIndex,  # ClaimIndex
    query_text: str,
    query_vector: List[Any],
    size: int,
    search_filter: Optional[SearchFilter] = None,
    sort_params: Optional[SortParams] = None,
    ranking_params: Optional[RankingParams] = None,
    use_vector_sim: bool = True,
    use_rescore: bool = True,
) -> Any:
    keyword_query = make_paper_keyword_search_query(
        query_text,
        search_filter=search_filter if search_filter else DEFAULT_SEARCH_CONFIG.search_filter,
    )
    sort_params = sort_params if sort_params else DEFAULT_SEARCH_CONFIG.metadata_sort_params
    rescore = []
    if use_vector_sim:
        rescore.append(
            make_paper_similarity_search_rescore_query(
                query_embedding=query_vector,
                window_size=DEFAULT_SEARCH_CONFIG.vector_search_window_size,
                similarity_weight=sort_params.similarity_weight,
            )
        )
    if use_rescore:
        rescore.append(
            make_paper_sort_rescore_query(
                window_size=sort_params.window_size,
                citation_count_weight=sort_params.citation_count_weight,
                citation_count_min=sort_params.citation_count_min,
                citation_count_max=sort_params.citation_count_max,
                publish_year_weight=sort_params.publish_year_weight,
                publish_year_min=sort_params.publish_year_min,
                publish_year_max=sort_params.publish_year_max,
                best_quartile_weight=sort_params.best_quartile_weight,
                best_quartile_default=sort_params.best_quartile_default,
            )
        )
    request_fields = ["abstract", "title", "paper_id"] + RELEVANCE_FEATURES
    response = paper_index.es.search(
        index=paper_index.name,
        size=size,
        query=keyword_query,
        rescore=rescore if rescore else None,
        source=False,
        fields=request_fields,  # type: ignore [arg-type]
    )
    return response


def get_background_claim_ids(storage_client: StorageClient) -> List[str]:
    disputed = parse_disputed_data(storage_client=storage_client)
    known_background_claim_ids = list(disputed.known_background_claim_ids.keys())
    return known_background_claim_ids


def get_test_queries(
    embedding_model: SimilaritySearchEmbeddingModel,
    num_queries: int,
    quantize_vectors: bool = False,
) -> List[Tuple[str, str, list[Any]]]:
    cleaned_text_tuples = [
        (
            text,
            _clean_text(
                options=TextCleaningOptions(
                    remove_stopwords=TextType.KEYWORD,
                    remove_punctuation=None,
                ),
                text=text,
            ),
        )
        for text in SEARCH_TESTING_QUERY_LIST[:num_queries]
    ]
    text_vector_query_tuples = [
        (
            original_text,
            cleaned_text,
            (
                quantize_vector(encode_similarity_search_embedding(embedding_model, vector_text))
                if quantize_vectors
                else encode_similarity_search_embedding(embedding_model, vector_text)
            ),
        )
        for original_text, (cleaned_text, vector_text) in cleaned_text_tuples
    ]

    return text_vector_query_tuples  # type: ignore [return-value]


def _is_valid_blob(blob_name: str, paper_eval: bool) -> bool:
    _, ext = os.path.splitext(blob_name)
    if ext != ".csv":
        return False
    return (paper_eval and "/paper_eval/" in blob_name) or (
        not paper_eval and "/paper_eval/" not in blob_name
    )


def read_annotated_labels(storage_client: storage.Client, paper_eval: bool) -> pd.DataFrame:
    prefix = SEARCH_EVAL_ANNOTATIONS_OUTPUT_PREFIX
    if paper_eval:
        prefix = os.path.join(prefix, "paper_eval")
    blobs = storage_client.list_blobs(SEARCH_EVAL_BUCKET, prefix=prefix)

    files = [b.name for b in blobs if _is_valid_blob(b.name, paper_eval)]
    dfs = []
    for f in files:
        file_path = f"gs://{SEARCH_EVAL_BUCKET}/{f}"
        dfs.append(pd.read_csv(file_path))

    return pd.concat(dfs, ignore_index=True).drop(columns=["agreement", "case_id", "origin"])


# roughly copied from:
# https://github.com/Consensus-NLP/consensus_machine_learning/blob/4a8f15bedc42c6feb6f4abdbdb2ab4316743aaad/utils/metrics.py#L405
def get_centaur_labels() -> pd.DataFrame:
    gcs_label_path = SEARCH_EVAL_CENTAUR_LABELS_PATH
    gcs_upload_path = SEARCH_EVAL_CENTAUR_UPLOAD_PATH
    label_df = pd.read_csv(gcs_label_path)
    df = pd.read_csv(gcs_upload_path)
    label_df.columns = pd.Index([c.replace(" ", "_").lower() for c in label_df.columns])

    df = df.merge(label_df, how="inner", on="origin")

    if "text" in df:
        text_column = "text"
    elif "content" in df:
        text_column = "content"
    else:
        text_column = "html"
    df = df.loc[
        :, ["case_id", "origin", text_column, "labeling_state", "correct_label", "agreement"]
    ].copy()

    df = df[(df.labeling_state == "Labeled") | (df.labeling_state == "Gold Standard")].copy()
    df.drop("labeling_state", axis=1, inplace=True)

    df.loc[:, "query"] = df.loc[:, "html"].apply(lambda x: x[138 : x.find("</p")])  # noqa: E203
    df.loc[:, "answer"] = df.loc[:, "html"].apply(
        lambda x: x[x.find("Answer:") + 13 : x.find("</p> </div> </html>")]  # noqa: E203
    )
    df.drop(["html"], axis=1, inplace=True)

    df = df.drop_duplicates(subset=["query", "answer"])
    return df


# roughly copied from:
# https://github.com/Consensus-NLP/consensus_machine_learning/blob/4a8f15bedc42c6feb6f4abdbdb2ab4316743aaad/utils/metrics.py#L405
def merge_query_results_with_labels(
    query_results_df: pd.DataFrame,
    labels_df: pd.DataFrame,
    paper_eval: bool,
) -> pd.DataFrame:
    # claim evals use centaur labels, which don't have paper ids, so we join by query and answer
    if not paper_eval:
        # normalize query and answer columns for joining, since centaur does not have claim ids
        query_results_df[QUERY_COL] = query_results_df[QUERY_COL].str.lower().str.strip()
        query_results_df["answer"] = query_results_df["answer"].str.lower().str.strip()
        labels_df[QUERY_COL] = labels_df[QUERY_COL].str.lower().str.strip()
        labels_df["answer"] = labels_df["answer"].str.lower().str.strip()

        query_results_df = query_results_df.drop_duplicates(subset=[QUERY_COL, "answer"])
        labels_df = labels_df.drop_duplicates(subset=[QUERY_COL, "answer"])
        # outer join so we can compute recall metrics downstream
        query_results_df_join = query_results_df.merge(
            labels_df, how="outer", on=[QUERY_COL, "answer"], suffixes=(None, "_y")
        )
        # drop unneeded columns
        columns_to_drop = ["claim_id_y", "paper_id_y"]
    else:
        query_results_df_join = query_results_df.merge(
            labels_df, how="outer", on=[QUERY_COL, "paper_id"], suffixes=(None, "_y")
        )
        columns_to_drop = ["answer_y", "title_y"]
    # drop unneeded columns
    query_results_df_join.drop(
        columns_to_drop,
        axis=1,
        inplace=True,
    )
    # remove queries with no search results
    labelled_queries_df = query_results_df_join.groupby([QUERY_COL], as_index=False).filter(
        lambda x: x[RANK_COL].any()
    )
    return labelled_queries_df


# Returns true if there are unlabelled annotations to export, false otherwise
def export_unlabelled_annotations(df: pd.DataFrame, run_id: str, paper_eval: bool) -> bool:
    all_unannotated = df[df["correct_label"].isnull()].copy()
    base_columns = ["query", "pred_rank", "paper_id", "claim_id", "answer"]
    columns = base_columns + ["title", "doi"] if paper_eval else base_columns
    if len(all_unannotated) > 0:
        all_unannotated = all_unannotated.loc[:, columns].copy()
        annotations_file = f"{'paper_eval/' if paper_eval else ''}{run_id}.csv"
        unannotated_output_path = f"gs://{os.path.join(SEARCH_EVAL_BUCKET, SEARCH_EVAL_TO_ANNOTATE_PREFIX, annotations_file)}"  # noqa: E501
        all_unannotated.to_csv(
            unannotated_output_path,
            index=False,
        )
        logger.info(f"Uploaded unannotated query-claim pairs to: {unannotated_output_path}")
        logger.info(f"Total missing annotations: {len(all_unannotated)}")
        return True
    return False
