from dataclasses import asdict, dataclass
from typing import Any, Iterator, List

import apache_beam as beam  # type: ignore
import apache_beam.io.fileio as fileio  # type: ignore
import nltk
import pyarrow  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from common.beam.papers import read_papers_with_status
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.db.connect import DbEnv
from common.storage.connect import StorageEnv
from common.storage.datasets import get_new_dataset_id_and_path
from paper_pb2 import Paper, PaperStatus

MAX_ROWS_PER_OUTPUT_PARQUET = 150000


@dataclass(frozen=True)
class DataRow:
    paper_id: int
    sentence_id: int
    dataset_id: str
    clean_data_url: str
    sentence: str


DataRowSchema = pyarrow.schema(
    [
        ("paper_id", pyarrow.int64()),
        ("sentence_id", pyarrow.int16()),
        ("dataset_id", pyarrow.string()),
        ("clean_data_url", pyarrow.string()),
        ("sentence", pyarrow.string()),
    ]
)


@dataclass(frozen=True)
class PaperToReadableAbstractPair:
    paper: List[Paper]
    readable_abstract: List[fileio.ReadableFile]


@dataclass(frozen=True)
class ParseIntoDataRowsResult(PipelineResult):
    paper_id: str
    data_rows: List[DataRow]
    dry_run: bool


class ParseIntoDataRows(beam.DoFn):
    def __init__(
        self,
        dry_run: bool,
        dataset_id: str,
    ):
        self.dry_run = dry_run
        self.dataset_id = dataset_id

    def setup(self):
        nltk.download("punkt")

    def process(self, pair: PaperToReadableAbstractPair) -> Iterator[ParseIntoDataRowsResult]:
        if len(pair.paper) != 1 or len(pair.readable_abstract) != 1:
            yield ParseIntoDataRowsResult(
                paper_id="empty",
                data_rows=[],
                dry_run=self.dry_run,
                success=False,
                message="Bad pipeline pair input, "
                + f"found {len(pair.paper)} papers and {len(pair.readable_abstract)} abstracts.",
            )
            return
        paper = pair.paper[0]
        readable_abstract = pair.readable_abstract[0]

        try:
            text = readable_abstract.read_utf8()
            sentences = nltk.tokenize.sent_tokenize(text)
            data_rows = []
            for idx, sentence in enumerate(sentences):
                sentence_id = idx + 1  # convert to 1 based index
                data_rows.append(
                    DataRow(
                        paper_id=paper.id,
                        sentence_id=sentence_id,
                        dataset_id=self.dataset_id,
                        clean_data_url=readable_abstract.metadata.path,
                        sentence=sentence,
                    )
                )
            yield ParseIntoDataRowsResult(
                paper_id=str(paper.id),
                data_rows=data_rows,
                dry_run=self.dry_run,
                success=True,
                message=None,
            )
        except Exception as e:
            yield ParseIntoDataRowsResult(
                paper_id=str(paper.id),
                data_rows=[],
                dry_run=self.dry_run,
                success=False,
                message=str(e),
            )


def run_parse_into_dataset_pipeline(
    runner: str,
    project_id: str,
    beam_args: Any,
    config: PipelineConfig,
    dry_run: bool,
    db_env: DbEnv,
    storage_env: StorageEnv,
) -> None:
    pipeline_options = PipelineOptions(
        beam_args,
        runner=runner,
        job_name=config.job_name,
        temp_location=config.temp_dir,
        max_num_workers=config.max_num_workers,
    )
    pipeline_options.view_as(SetupOptions).save_main_session = True

    dataset_id, dataset_path = get_new_dataset_id_and_path(env=storage_env)

    with beam.Pipeline(options=pipeline_options) as p:
        paper_protos = read_papers_with_status(
            p,
            db_env,
            project_id,
            PaperStatus.Status.CLEANED,
        )

        # Pair clean data URLs to papers
        paper_pairs = paper_protos | "PairPapersToFilenames" >> beam.Map(
            lambda paper: (paper.clean_data_url, paper)
        )

        # Pair clean data URLs to readable files for the URLs
        readable_abstract_pairs = (
            paper_protos
            | "GetCleanDataUrl" >> beam.Map(lambda paper: paper.clean_data_url)
            | "MatchCleanDataUrls" >> fileio.MatchAll()
            | "CreateReadableFilesForCleanData" >> fileio.ReadMatches()
            | "CreatePairs"
            >> beam.Map(
                lambda readable_abstract: (readable_abstract.metadata.path, readable_abstract)
            )
        )

        # Parse paper abstracts into dataset rows
        results = (
            (
                {
                    "paper": paper_pairs,
                    "readable_abstract": readable_abstract_pairs,
                }
            )
            | "GroupPairsByCleanDataUrl" >> beam.CoGroupByKey()
            | "ExtractPair" >> beam.Map(lambda x: PaperToReadableAbstractPair(**x[1]))
            | "ParseIntoDataRows"
            >> beam.ParDo(ParseIntoDataRows(dry_run=dry_run, dataset_id=dataset_id))
        )

        # Write dataset out to file
        if not dry_run:
            (
                results
                | "ExtractDataRow" >> beam.FlatMap(lambda result: result.data_rows)
                | "ConvertToDict" >> beam.Map(lambda data_row: asdict(data_row))
                | "WriteToParquet"
                >> beam.io.WriteToParquet(
                    file_path_prefix=dataset_path,
                    schema=DataRowSchema,
                    # Set row_group_buffer_size=1 to configure the row group
                    # size based on number of records in record_batch_size.
                    row_group_buffer_size=1,
                    record_batch_size=MAX_ROWS_PER_OUTPUT_PARQUET,
                )
            )

        write_pipeline_results(config.results_file, results, individual_failures_only=True)
