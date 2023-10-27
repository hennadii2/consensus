from common.beam.pipeline_config import PipelineConfig, get_pipeline_config


def test_get_pipeline_config_returns_expected_config() -> None:
    pipeline = "test-pipeline"

    actual = get_pipeline_config(pipeline)
    timestamp = actual.timestamp.strftime("%y%m%d%H%M%S")
    bucket = "gs://consensus-pipeline-logs"
    expected = PipelineConfig(
        job_name=f"test-pipeline-{timestamp}",
        temp_dir=f"{bucket}/temp/{pipeline}",
        results_file=f"{bucket}/results/{pipeline}/{pipeline}-{timestamp}/{pipeline}-{timestamp}",
        timestamp=actual.timestamp,
        max_num_workers=70,
    )
    assert actual == expected
