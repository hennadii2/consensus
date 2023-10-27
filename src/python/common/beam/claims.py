import os
from dataclasses import dataclass
from random import randint
from typing import Iterator

import apache_beam as beam  # type: ignore
from claim_pb2 import Claim, ClaimNamespace
from common.beam.model_outputs import ModelOutput, read_qualifying_model_outputs_from_parquet
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv, MainDbClient
from common.db.papers import Papers
from common.search.claim_util import generate_base_claim


@dataclass(frozen=True)
class ClaimWithCountId:
    count_id: int
    claim: Claim


class ModelOutputToClaimWithCountId(beam.DoFn):
    """
    DoFn to output claims from model output.
    """

    def __init__(
        self,
        db_env: DbEnv,
        project_id: str,
        max_items: int,
    ):
        self.db_env = db_env
        self.project_id = project_id
        self.max_items = max_items

    def setup(self):
        # Set GCLOUD_PROJECT_ID in worker to enable access to secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

        db = MainDbClient(self.db_env)
        self.papers = Papers(db)

    def teardown(self):
        self.papers.connection.close()

    def process(
        self,
        model_output: ModelOutput,
    ) -> Iterator[ClaimWithCountId]:
        paper_id = model_output.paper_id
        try:
            paper = self.papers.read_by_id(paper_id)
            if not paper:
                raise ValueError("Failed to find paper for id {paper_id}")

            claim = generate_base_claim(
                namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
                display_text=model_output.modified_claim,
                original_text=model_output.sentence,
                probability=model_output.claim_probability,
                paper_id=paper.paper_id,
                paper_metadata=paper.metadata,
                is_enhanced=False,
            )

            current_index = randint(0, self.max_items - 1)
            claim_with_count_id = ClaimWithCountId(
                claim=claim,
                count_id=current_index,
            )
            yield claim_with_count_id
        except Exception:
            pass


def read_claims_with_count_id_from_parquet(
    p: beam.Pipeline,
    input_file_pattern: str,
    db_env: DbEnv,
    project_id: str,
    total_num_claims: int,
) -> beam.PCollection[ClaimWithCountId]:
    """
    Helper function to read model output from parquet into a dataclass.
    """
    model_outputs = read_qualifying_model_outputs_from_parquet(p, input_file_pattern)
    claims_with_count_id = model_outputs | "FilterToModelOutputToClaimWithCountId" >> beam.ParDo(
        ModelOutputToClaimWithCountId(
            db_env=db_env,
            project_id=project_id,
            max_items=total_num_claims,
        )
    )
    return claims_with_count_id
