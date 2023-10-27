from __future__ import annotations

import os
from typing import Any, Iterator, NamedTuple, Optional

import apache_beam as beam  # type: ignore
import apache_beam.io.jdbc as jdbc  # type: ignore
from apache_beam import coders
from apache_beam.typehints.schemas import LogicalType  # type: ignore
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv, MainDbClient, get_jdbc_connection_info
from common.db.papers import PAPERS_TABLE, Papers, papers_row_to_proto
from paper_pb2 import Paper, PaperStatus


class ReadPapersWithStatusDoFn(beam.DoFn):
    """
    DoFn to read all DB rows in the papers table with a given status.
    """

    def __init__(self, db_env: DbEnv, project_id: str, status: PaperStatus.Status.V):
        self.db_env = db_env
        self.project_id = project_id
        self.status = status

    def setup(self):
        # Set GCLOUD_PROJECT_ID in worker to enable access to secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

        connection = MainDbClient(self.db_env)
        self.db = Papers(connection)

    def teardown(self):
        self.db.connection.close()

    def process(self, p) -> Iterator[Paper]:
        yield from self.db.read_all_with_status(self.status)


def read_papers_with_status(
    p: beam.Pipeline, db_env: DbEnv, project_id: str, status: PaperStatus.Status.V
) -> beam.PCollection[Paper]:
    """
    Helper function to read all papers from the DB using a workaround instead
    of jdbc, which is not currently working (TODO: meganvw).
    """
    paper_protos = (
        p
        | "Workaround" >> beam.Create([""])
        | "ReadAllPapersFromDb" >> beam.ParDo(ReadPapersWithStatusDoFn(db_env, project_id, status))
        | "ReshuffleForFanout" >> beam.transforms.util.Reshuffle()
    )
    return paper_protos


def read_papers_with_status_jdbc_not_working(
    p: beam.Pipeline, db_env: DbEnv, status: PaperStatus.Status.V
) -> beam.PCollection[Any]:
    @LogicalType.register_logical_type
    class db_str(LogicalType):
        @classmethod
        def urn(cls):
            return "beam:logical_type:javasdk:v1"

        @classmethod
        def language_type(cls):
            return str

        def to_language_type(self, value):
            return str(value)

        def to_representation_type(self, value):
            return str(value)

    @LogicalType.register_logical_type
    class db_timestamp(LogicalType):
        @classmethod
        def urn(cls):
            return "beam:logical_type:datetime:v1"

        @classmethod
        def language_type(cls):
            return str

        def to_language_type(self, value):
            return str(value)

        def to_representation_type(self, value):
            return str(value)

    info = get_jdbc_connection_info(db_env)
    config_error = f"Failed to connect to jdbc for env {db_env}"
    if not info.url:
        raise ValueError(f"{config_error}: url is none")
    if not info.user:
        raise ValueError(f"{config_error}: user is none")
    if not info.password:
        raise ValueError(f"{config_error}: password is none")

    class PapersRow(NamedTuple):
        id: int
        raw_data_url: str
        clean_data_url: Optional[str]
        status: bytes
        metadata: bytes
        created_at: str
        last_updated_at: str

    coders.registry.register_coder(PapersRow, coders.RowCoder)

    paper_protos = (
        p
        | "ReadAllFromPapersDb"
        >> jdbc.ReadFromJdbc(
            table_name=PAPERS_TABLE,
            driver_class_name="org.postgresql.Driver",
            jdbc_url=info.url,
            username=info.user,
            password=info.password,
            # There is a bug in apache-beam[gcp]=2.37.0 that the composite
            # jar creation does not correctly create the MANIFEST (appends
            # classpath using spaces instead of newlines, so the line gets too
            # long and fails), so we self-create a fat/uber jar that includes
            # all requried dependencies as a workaround and pass it in here.
            classpath=["/root/uber-postgres-socket-factory.jar"],
        )
        | "PapersRowToProto" >> beam.Map(lambda row: papers_row_to_proto(row))
        | "FilterForPaperStatus" >> beam.Filter(lambda paper: paper.status.status == status)
    )
    return paper_protos
