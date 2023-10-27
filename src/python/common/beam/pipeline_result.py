import json
from dataclasses import asdict, dataclass
from typing import Any, Callable, Optional

import apache_beam as beam  # type: ignore
import apache_beam.io.textio as textio  # type: ignore


def _simplify_message(message: Optional[str]) -> Optional[str]:
    """
    Returns a simplified version of a log message if possible. This is useful to
    better group similar results in a summary file.
    """
    if not message:
        return message

    utf8_error = "'utf-8' codec can't decode byte"
    if message.startswith(utf8_error):
        return utf8_error

    sanitize_error = "Failed to sanitize text for stable ID: field is too short:"
    if message.startswith(sanitize_error):
        return sanitize_error

    return message


@dataclass(frozen=True)
class PipelineResult:
    """
    Base dataclass used by write_pipeline_results.
    """

    success: bool
    message: Optional[str]


def no_op_filter(x: Any) -> bool:
    return True


def write_pipeline_results(
    output_file: str,
    results: beam.PCollection[PipelineResult],
    individual_failures_only=True,
    custom_filter_for_individual_results: Optional[Callable[[PipelineResult], bool]] = None,
) -> None:
    """
    Helper to generate a summary of pipeline results and write them to file.

    Pipeline results are dataclass messages of work completed by the pipeline,
    not usable output that the pipeline generates.
    """
    if custom_filter_for_individual_results is None:
        custom_filter_for_individual_results = no_op_filter

    if individual_failures_only:
        # Write only individual failure results to file
        (
            results
            | "FilterForFailuresOnly" >> beam.Filter(lambda x: not x.success)
            | "CustomFilter" >> beam.Filter(custom_filter_for_individual_results)
            | "PipelineResultsToString" >> beam.Map(lambda x: json.dumps(asdict(x)))
            | "WritePipelineResults" >> textio.WriteToText(output_file)
        )
    else:
        # Write all individual results to file (successes and failures)
        (
            results
            | "CustomFilter" >> beam.Filter(custom_filter_for_individual_results)
            | "PipelineResultsToString" >> beam.Map(lambda x: json.dumps(asdict(x)))
            | "WritePipelineResults" >> textio.WriteToText(output_file)
        )

    # Write summary of results to file
    summary_output_file = f"{output_file}-summary"
    (
        results
        | "SimplifyPipelineResults"
        >> beam.Map(lambda x: (x.success, _simplify_message(x.message)))
        | "CountGroupedPipelineResults" >> beam.combiners.Count.PerElement()
        | "CountResultsToString"
        >> beam.Map(
            lambda x: json.dumps(
                {
                    "success": x[0][0],
                    "message": x[0][1],
                    "count": x[1],
                }
            )
        )
        | "WritePipelineResultsSummary" >> textio.WriteToText(summary_output_file)
    )
