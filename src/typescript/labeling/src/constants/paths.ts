const QA_SEARCH_BUCKET_PATH = "consensus-nlp-models/search";

/** GCS path where search testing results are stored. */
export const QA_METRICS_BUCKET_PATH = `${QA_SEARCH_BUCKET_PATH}/search_testing/metrics`;

/** GCS path where un-annotated files from search testing are stored. */
export const QA_TO_ANNOTATE_BUCKET_PATH = `${QA_SEARCH_BUCKET_PATH}/search_testing/to_annotate`;
export const QA_TO_ANNOTATE_PAPER_BUCKET_PATH = `${QA_SEARCH_BUCKET_PATH}/search_testing/to_annotate/paper_eval`;

/** GCS path to write out new annotations. */
export const QA_ANNOTATED_BUCKET_PATH = `${QA_SEARCH_BUCKET_PATH}/annotation_outputs/internal_annotations_editor`;
export const QA_ANNOTATED_PAPER_BUCKET_PATH = `${QA_SEARCH_BUCKET_PATH}/annotation_outputs/internal_annotations_editor/paper_eval`;
