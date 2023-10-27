import csv
import gzip
import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone

import git
import nltk
from claim_pb2 import ClaimNamespace
from common.beam.records.base_record import RecordStatus
from common.cache.redis_connection import RedisConnection, RedisEnv
from common.config.constants import (
    REPO_PATH_LOCAL_DOT_ENV,
    REPO_PATH_MAIN_SQL,
    REPO_PATH_MOCK_DATA_AUTOCOMPLETE_QUERIES,
    REPO_PATH_MOCK_DATA_SEMANTIC_SCHOLAR,
    REPO_PATH_WEB_DATA_DISPUTED_JSON,
)
from common.db.abstract_takeaways import AbstractTakeaways, TakeawayMetrics
from common.db.claim_ids_to_paper_ids import ClaimIdsToPaperIds
from common.db.connect import DbEnv, MainDbClient
from common.db.hash_paper_ids import HashPaperIds
from common.db.journal_scores import JournalScores
from common.db.journals import Journals
from common.db.paper_inferences import PaperInferences
from common.db.papers import Papers
from common.db.records.abstract_records import AbstractRecords
from common.db.records.paper_records import PaperRecords
from common.ingestion.extract import (
    extract_metadata_and_abstract,
    filter_metadata_for_ingestion,
    filter_metadata_for_product,
)
from common.models.similarity_search_embedding import (
    SimilaritySearchEmbeddingModel,
    encode_similarity_search_embedding,
    initialize_similarity_search_embedding_model,
)
from common.search.autocomplete_index import AutocompleteIndex
from common.search.claim_index import ClaimIndex
from common.search.claim_util import generate_claim
from common.search.connect import ElasticClient, SearchEnv
from common.search.paper_index import PaperIndex
from common.search.paper_util import PaperIdProvider, generate_hash_paper_id, generate_paper
from dotenv import load_dotenv
from journal_pb2 import JournalScoreMetadata, JournalScoreProvider
from loguru import logger
from nltk import tokenize
from paper_inferences_pb2 import InferenceData, PaperInference
from paper_metadata_pb2 import PaperProvider
from paper_pb2 import Paper

OUTPUT_DIR_CLEANED_DATA = "data/.mockdata"
WITH_SPLIT_TITLE_EMBEDDING = True
MOCK_JOB_NAME = "ingest_mock_data"
MOCK_COVID_ANSWERS = [
    "Vaccines are effective against covid-19 [mock data].",
    "Studies show that vaccines are effective against covid-19 [mock data].",
    "Research indicates that vaccines are effective against covid-19 [mock data].",
    "Vaccines are tested to be effective against covid-19 [mock data].",
    "Vaccines are not effective against covid-19 [mock data].",
    "Studies show that vaccines are not effective against covid-19 [mock data].",
    "Research indicates that vaccines are not effective against covid-19 [mock data].",
    "Vaccines are not tested to be effective against covid-19 [mock data].",
]


@dataclass(frozen=True)
class MockJournal:
    name: str
    percentile_rank: float


MOCK_JOURNALS_AND_SCORES: list[MockJournal] = [
    MockJournal(name="Psychophysiology", percentile_rank=0.5),
    MockJournal(name="Journal of Sports Sciences", percentile_rank=0.8),
    MockJournal(name="Tetrahedron Letters", percentile_rank=0.2),
    MockJournal(name="Polymer Chemistry", percentile_rank=0.6),
    MockJournal(name="Journal of Geophysical Research", percentile_rank=0.9),
]


@dataclass(frozen=True)
class MockStudyDetails:
    paper_id: int
    # study types
    prediction: str
    new: str
    # other study details
    population_type: str
    sample_size: int
    study_count: int


MOCK_STUDY_DETAILS: dict[str, MockStudyDetails] = {
    "e3d68a8fb8df5c2b93ba01e725ab61ce": MockStudyDetails(
        paper_id=448,
        prediction="RCT Study",
        new="rct",
        population_type="human",
        sample_size=300,
        study_count=0,
    ),
    "d79353a8c7385543811a0a19739c59b5": MockStudyDetails(
        paper_id=144,
        prediction="Meta Analysis",
        new="meta-analysis",
        population_type="",
        sample_size=0,
        study_count=0,
    ),
    "7003ad38affe5a498709f958a5914eb8": MockStudyDetails(
        paper_id=470,
        prediction="Case Report",
        new="case report",
        population_type="animal",
        sample_size=0,
        study_count=400,
    ),
    "c4b44202d55a556d9e871134be3eab6a": MockStudyDetails(
        paper_id=173,
        prediction="Systematic Review",
        new="systematic review",
        population_type="human",
        sample_size=300,
        study_count=0,
    ),
    "d61a543173f45d88af6b3ce29acfb491": MockStudyDetails(
        paper_id=451,
        prediction="RCT Study",
        new="rct",
        population_type="animal",
        sample_size=0,
        study_count=0,
    ),
}

MOCK_DISPUTED_JSON = {
    "disputed_papers": [
        {
            "key": "test1",
            "reason": "The majority of research refutes this TEST1 topic.",
            "url": "https://consensus.app/#",
            "paper_ids": ["458", "276"],
        },
        {
            "key": "test2",
            "reason": "The majority of research refutes this TEST2 topic.",
            "url": "https://consensus.app/#",
            "paper_ids": ["148", "276"],
        },
        {
            "key": "test3",
            "reason": "The majority of research agrees with this TEST3 topic.",
            "url": "https://consensus.app/#",
            "paper_ids": ["451"],
        },
    ],
    "known_background_claim_ids": [],
}

# Required for sentence tokenization
nltk.download("punkt")


def init_local_databases() -> tuple[Papers, Journals, JournalScores, PaperInferences]:
    """
    Drops all tables in the database and recreates them with the latest sql.
    """
    cxn = MainDbClient(DbEnv.LOCAL)
    assert cxn.info.host == "localhost"

    with cxn.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS papers;")
        cursor.execute("DROP TABLE IF EXISTS paper_inferences;")
        cursor.execute("DROP TABLE IF EXISTS journals;")
        cursor.execute("DROP TABLE IF EXISTS journal_scores;")
        cursor.execute("DROP TABLE IF EXISTS bookmark_items;")
        cursor.execute("DROP TYPE IF EXISTS bookmark_type;")
        cursor.execute("DROP TABLE IF EXISTS bookmark_lists;")
        cursor.execute("DROP TABLE IF EXISTS abstract_takeaways;")
    cxn.commit()

    with cxn.cursor() as cursor:
        with open(REPO_PATH_MAIN_SQL) as main_sql_file:
            sql = main_sql_file.read()
            cursor.execute(sql)
    cxn.commit()
    return (Papers(cxn), Journals(cxn), JournalScores(cxn), PaperInferences(cxn))


def initialize_local_elasticsearch() -> tuple[ClaimIndex, AutocompleteIndex, PaperIndex]:
    """
    Drops all indexes in elasticsearch and recreates them with the latest mappings.
    """
    es = ElasticClient(SearchEnv.LOCAL)
    claim_index = ClaimIndex(es, "mock-data")
    claim_index.create(delete_if_exists=True)
    autocomplete_index = AutocompleteIndex(es, "mock-data")
    autocomplete_index.create(delete_if_exists=True)
    paper_index = PaperIndex(es, "mock-data-paper-search")
    paper_index.create(delete_if_exists=True)
    return (claim_index, autocomplete_index, paper_index)


def initialize_local_data_dir() -> tuple[str, str]:
    """
    Creates a directory at the root of your local git repo to hold processed
    mock data, deleting previous mock data if any exists, and returns the path.
    """
    repo = git.Repo(".", search_parent_directories=True)
    root = str(repo.working_tree_dir)
    output_dir = os.path.join(root, OUTPUT_DIR_CLEANED_DATA)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)
    return root, output_dir


def clear_redis_cache() -> None:
    """Deletes all cached data."""
    redis = RedisConnection(RedisEnv.LOCAL)
    redis.flushdb()


def clean_abstract_text(text: str) -> str:
    # TODO(meganvw): Call cleaning function once its added
    return text


def write_mock_paper_to_v2(
    paper: Paper,
    paper_records_db: PaperRecords,
    abstract_records_db: AbstractRecords,
    timestamp: datetime,
    job_name: str,
    commit: bool,
) -> None:
    paper_records_db.write_record(
        paper_id=paper.paper_id,
        version="version_1",
        metadata=paper.metadata,
        status=RecordStatus.ACTIVE,
        status_msg=None,
        input_data_hash="input_data_hash",
        method_version_hash="method_version_hash",
        job_name=job_name,
        timestamp=timestamp,
        commit=commit,
    )
    abstract_records_db.write_record(
        paper_id=paper.paper_id,
        version="version_1",
        gcs_abstract_url=paper.clean_data_url,
        status=RecordStatus.ACTIVE,
        status_msg=None,
        method_version_hash="method_version_hash",
        input_data_hash="input_data_hash",
        job_name=job_name,
        timestamp=timestamp,
        commit=commit,
    )


def ingest_semantic_scholar_compressed_file(
    db: Papers,
    claim_index: ClaimIndex,
    paper_index: PaperIndex,
    embedding_model: SimilaritySearchEmbeddingModel,
    input_path: str,
    output_dir_cleaned: str,
    number_to_ingest: int = 500,
) -> int:
    """
    Adds semantic scholar mock data to the papers table and claim search index.

    The first sentence of the abstract is used as the claim.
    """
    paper_records_db = PaperRecords(connection=db.connection)
    abstract_records_db = AbstractRecords(connection=db.connection)
    abstract_takeaways_db = AbstractTakeaways(connection=db.connection)
    claim_ids_to_paper_ids_db = ClaimIdsToPaperIds(connection=db.connection)
    hash_paper_ids = HashPaperIds(connection=db.connection)
    timestamp = datetime.now(tz=timezone.utc)

    success_count = 0
    with gzip.open(input_path, "rt") as mock_data_file:
        for index, line in enumerate(mock_data_file):
            if index >= number_to_ingest:
                break

            metadata, abstract = extract_metadata_and_abstract(
                PaperProvider.SEMANTIC_SCHOLAR, line
            )
            if abstract is None:
                continue

            # Filter for ingestion requirements
            try:
                filter_metadata_for_ingestion(metadata)
            except Exception:
                continue

            cleaned = clean_abstract_text(abstract)
            # TODO(meganvw): Clean up calls writing to old Papers table
            paper = db.write_paper(
                raw_data_url=input_path,
                metadata=metadata,
                provider_metadata={},
                job_name=MOCK_JOB_NAME,
                timestamp=None,
                commit=False,
                update_if_exists=False,
            )

            # Filter for product requirements
            try:
                filter_metadata_for_product(metadata)
            except Exception:
                continue

            output_filepath = os.path.join(
                output_dir_cleaned,
                str(paper.paper_id),
                "abstract",
            )
            os.makedirs(os.path.dirname(output_filepath))
            with open(output_filepath, "w") as clean_data_file:
                clean_data_file.write(cleaned)
            paper = db.update_clean_data_url(
                paper_id=paper.id,
                clean_data_url=output_filepath,
                abstract=abstract,
                job_name=MOCK_JOB_NAME,
                timestamp=None,
                commit=False,
            )

            # Update mock paper_id to S2 format required by generate_hash_paper_id
            paper.paper_id = f"S2:{paper.id}"
            write_mock_paper_to_v2(
                paper=paper,
                paper_records_db=paper_records_db,
                abstract_records_db=abstract_records_db,
                timestamp=timestamp,
                job_name=MOCK_JOB_NAME,
                commit=False,
            )

            sentences = tokenize.sent_tokenize(cleaned)
            if not len(sentences):
                continue

            # add last sentence as a "claim"
            text = sentences[-1]
            force_mock_data = False
            # add more results that will return on the term "covid" for
            # testing purposes
            if success_count < len(MOCK_COVID_ANSWERS):
                text = MOCK_COVID_ANSWERS[success_count]
                force_mock_data = True

            try:
                claim = generate_claim(
                    embedding_model=embedding_model,
                    namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
                    display_text=text,
                    original_text=text,
                    probability=1.0,
                    paper=paper,
                    with_split_title_embedding=WITH_SPLIT_TITLE_EMBEDDING,
                )
                if claim.id in MOCK_STUDY_DETAILS:
                    claim.metadata.study_type = MOCK_STUDY_DETAILS[claim.id].new
                    claim.metadata.sample_size = MOCK_STUDY_DETAILS[claim.id].sample_size
                    claim.metadata.study_count = MOCK_STUDY_DETAILS[claim.id].study_count
                    claim.metadata.population_type = MOCK_STUDY_DETAILS[claim.id].population_type
                claim_index.add_claim(
                    claim,
                    with_split_title_embedding=WITH_SPLIT_TITLE_EMBEDDING,
                )

                title_astract_embedding = encode_similarity_search_embedding(
                    embedding_model,
                    f"{paper.metadata.title} {text}",
                )
                study_type = claim.metadata.study_type if claim.metadata.study_type else None

                # Write paper to elastic search
                paper_doc = generate_paper(
                    hash_paper_id=generate_hash_paper_id(PaperIdProvider.S2, paper.paper_id),
                    paper_id=paper.paper_id,
                    abstract=text if force_mock_data else abstract,
                    paper_metadata=paper.metadata,
                    title_abstract_embedding=title_astract_embedding,
                    study_type=study_type,
                    sjr_best_quartile=None,
                )
                paper_index.add_paper(paper=paper_doc)

                # Write claim as abstract takeaway to DB
                abstract_takeaways_db.write_takeaway(
                    paper_id=paper_doc.paper_id,
                    takeaway=f"{text} [takeaway]",
                    metrics=TakeawayMetrics(
                        takeaway_to_title_abstract_r1r=1.0,
                        takeaway_length=100,
                        takeaway_distinct_pct=1.0,
                        takeaway_non_special_char_pct=1.0,
                        abstract_length=100,
                        abstract_distinct_pct=1.0,
                        abstract_non_special_char_pct=100,
                    ),
                    job_name=MOCK_JOB_NAME,
                    commit=False,
                )
                claim_ids_to_paper_ids_db.write_claim_id_to_paper_id(
                    claim_id=claim.id,
                    paper_id=paper.paper_id,
                    job_name=MOCK_JOB_NAME,
                    commit=False,
                )
                hash_paper_ids.write_mapping(
                    paper_id=paper_doc.paper_id,
                    hash_paper_id=paper_doc.hash_paper_id,
                    timestamp=datetime.now(tz=timezone.utc),
                    job_name=MOCK_JOB_NAME,
                    commit=False,
                )
            except Exception as e:
                logger.error(e)

            claim_index.refresh()
            paper_index.refresh()

            success_count += 1
    db.connection.commit()
    return success_count


def ingest_mock_journal_data(
    journals_db: Journals,
    journal_scores_db: JournalScores,
) -> int:
    """
    Adds mock journal data to the journals and journal scores tables.
    """

    success_count = 0
    for mock_data in MOCK_JOURNALS_AND_SCORES:
        journal = journals_db.write_journal(
            name=mock_data.name,
            print_issn=None,
            electronic_issn=None,
            job_name=MOCK_JOB_NAME,
        )
        metadata = JournalScoreMetadata()
        metadata.computed_score.percentile_rank = mock_data.percentile_rank
        for year in range(1990, 2022):
            journal_scores_db.write_score(
                journal_id=journal.id,
                year=year,
                provider=JournalScoreProvider.COMPUTED,
                metadata=metadata,
                job_name=MOCK_JOB_NAME,
            )
        success_count += 1
    journals_db.connection.commit()
    return success_count


def ingest_mock_paper_inferences(
    paper_inferences_db: PaperInferences,
) -> int:
    """
    Adds mock paper inferences to the database.
    """

    success_count = 0
    for mock_data in MOCK_STUDY_DETAILS.values():
        inference_data = InferenceData()
        study_type = inference_data.study_type.values.add()
        study_type.prediction = mock_data.prediction
        paper_inferences_db.write(
            paper_id=mock_data.paper_id,
            provider=PaperInference.Provider.CONSENSUS,
            inference_data=inference_data,
            source="mock_source",
            job_name=MOCK_JOB_NAME,
            timestamp=datetime.now(tz=timezone.utc),
            commit=False,
        )
        success_count += 1
    paper_inferences_db.connection.commit()
    return success_count


def ingest_autocomplete_data(
    autocomplete_index: AutocompleteIndex,
    input_path: str,
    number_to_ingest: int = 500,
) -> int:
    """
    Adds mock autocomplete data to the elasticsearch index.
    """

    success_count = 0
    with open(input_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            query = row["Result"].strip()
            autocomplete_index.add_query(query, preferred=(success_count % 5 == 0))
            success_count += 1
            if success_count >= number_to_ingest:
                break
    autocomplete_index.refresh()
    return success_count


def write_mock_data_overrides(
    output_dir: str,
) -> None:
    """
    Adds mock paper inferences to the database.
    """

    disputed_filepath = os.path.join(output_dir, REPO_PATH_WEB_DATA_DISPUTED_JSON)
    with open(disputed_filepath, "w") as disputed_file:
        disputed_file.write(json.dumps(MOCK_DISPUTED_JSON))
    logger.info(f"Overwrote mock data at {disputed_filepath}")


def main():
    """
    Ingest mock data into the local DB and filesystem.

    WARNING: This is a desctructive method. The DB and cleaned data directories
    will be destroyed and recreated.
    """

    load_dotenv(REPO_PATH_LOCAL_DOT_ENV)
    papers, journals, journal_scores, paper_inferences = init_local_databases()
    claim_index, autocomplete_index, paper_index = initialize_local_elasticsearch()
    embedding_model = initialize_similarity_search_embedding_model()

    output_root_dir, output_mock_data_dir = initialize_local_data_dir()
    write_mock_data_overrides(output_dir=output_root_dir)

    clear_redis_cache()
    logger.info("Deleted redis cache")

    logger.info(f"Output dir is {output_mock_data_dir}")
    success_count = ingest_autocomplete_data(
        input_path=REPO_PATH_MOCK_DATA_AUTOCOMPLETE_QUERIES,
        autocomplete_index=autocomplete_index,
    )
    logger.info(f"Added {success_count} autocomplete queries to elasticsearch")
    success_count = ingest_semantic_scholar_compressed_file(
        db=papers,
        claim_index=claim_index,
        paper_index=paper_index,
        embedding_model=embedding_model,
        input_path=REPO_PATH_MOCK_DATA_SEMANTIC_SCHOLAR,
        output_dir_cleaned=os.path.join(output_mock_data_dir, "cleaned"),
    )
    logger.info(f"Added {success_count} papers and claims to the database")
    success_count = ingest_mock_journal_data(
        journals_db=journals,
        journal_scores_db=journal_scores,
    )
    logger.info(f"Added {success_count} journals and scores to the database")
    success_count = ingest_mock_paper_inferences(
        paper_inferences_db=paper_inferences,
    )
    logger.info(f"Added {success_count} paper inferences to the database")


if __name__ == "__main__":
    main()
