from datetime import datetime, timedelta, timezone

import pytest  # type: ignore
from common.db.paper_inferences import PAPER_INFERENCES_TABLE, PaperInferences
from common.db.paper_inferences_util import StudyTypeEnum
from common.db.test.connect import MainDbTestClient
from google.protobuf.json_format import MessageToDict
from paper_inferences_pb2 import InferenceData, PaperInference


def mock_data(prediction: str) -> InferenceData:
    data = InferenceData()
    study_type = data.study_type.values.add()
    study_type.prediction = prediction
    study_type.probability = 0.5
    return data


@pytest.fixture
def connection():
    with MainDbTestClient() as connection:
        yield connection


def test_write_score_succeeds(connection) -> None:
    timestamp = datetime.now(timezone.utc)
    fmt = "%y%m%d%H%M%S%.f"

    db = PaperInferences(connection)
    data = mock_data("Case Study")
    db.write(
        paper_id=10,
        provider=PaperInference.Provider.CONSENSUS,
        inference_data=data,
        source="model_output",
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {PAPER_INFERENCES_TABLE}")
        results = cursor.fetchall()

        assert len(results) == 1

        actual = results[0]

        assert actual["id"] == 1
        assert actual["paper_id"] == 10
        assert actual["type"] == "STUDY_TYPE"
        assert actual["provider"] == "CONSENSUS"
        assert actual["source"] == "model_output"
        assert actual["data"] == MessageToDict(data, preserving_proto_field_name=True)
        assert actual["created_at"].strftime(fmt) == timestamp.strftime(fmt)
        assert actual["created_by"] == "test_job"


def test_get_inferences_returns_latest_provider_entry(connection) -> None:
    now = datetime.now(timezone.utc)
    later = now + timedelta(minutes=10)

    db = PaperInferences(connection)
    data1 = mock_data("Case Study")
    consensus_inference1 = db.write(
        paper_id=10,
        provider=PaperInference.Provider.CONSENSUS,
        inference_data=data1,
        source="source1",
        job_name="job1",
        timestamp=now,
        commit=True,
    )
    s2_inference = db.write(
        paper_id=10,
        provider=PaperInference.Provider.SEMANTIC_SCHOLAR,
        inference_data=data1,
        source="source1",
        job_name="job2",
        timestamp=now,
        commit=True,
    )
    data2 = mock_data("RCT Study")
    consensus_inference2 = db.write(
        paper_id=10,
        provider=PaperInference.Provider.CONSENSUS,
        inference_data=data2,
        source="source2",
        job_name="job2",
        timestamp=later,
        commit=True,
    )
    assert consensus_inference1 != consensus_inference2
    expected = [consensus_inference2, s2_inference]
    actual = db.get_inferences(
        paper_id=10,
        inference_type=PaperInference.Type.STUDY_TYPE,
    )
    assert actual == expected


def test_get_study_type(connection) -> None:
    now = datetime.now(timezone.utc)

    db = PaperInferences(connection)
    db.write(
        paper_id=10,
        provider=PaperInference.Provider.CONSENSUS,
        inference_data=mock_data("Case Report"),
        source="source1",
        job_name="job1",
        timestamp=now,
        commit=True,
    )

    actual = db.get_study_type(paper_id=10)
    assert actual == StudyTypeEnum.CASE_REPORT


def test_get_study_type_with_provider_metadata(connection) -> None:
    now = datetime.now(timezone.utc)

    db = PaperInferences(connection)
    db.write(
        paper_id=10,
        provider=PaperInference.Provider.CONSENSUS,
        inference_data=mock_data("RCT Study"),
        source="source1",
        job_name="job1",
        timestamp=now,
        commit=True,
    )

    s2_metadata = '{"publicationtypes": ["CaseReport"]}'
    actual = db.get_study_type(paper_id=10, provider_metadata=s2_metadata)
    assert actual == StudyTypeEnum.CASE_REPORT


def test_get_study_type_with_provider_metadata_null(connection) -> None:
    now = datetime.now(timezone.utc)

    db = PaperInferences(connection)
    db.write(
        paper_id=10,
        provider=PaperInference.Provider.CONSENSUS,
        inference_data=mock_data("RCT Study"),
        source="source1",
        job_name="job1",
        timestamp=now,
        commit=True,
    )

    s2_metadata = '{"publicationtypes": null}'
    actual = db.get_study_type(paper_id=10, provider_metadata=s2_metadata)
    assert actual == StudyTypeEnum.RCT_STUDY
