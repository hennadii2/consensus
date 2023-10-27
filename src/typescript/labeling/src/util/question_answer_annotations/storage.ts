import {
  QA_ANNOTATED_BUCKET_PATH,
  QA_ANNOTATED_PAPER_BUCKET_PATH,
  QA_METRICS_BUCKET_PATH,
  QA_TO_ANNOTATE_BUCKET_PATH,
  QA_TO_ANNOTATE_PAPER_BUCKET_PATH,
} from "constants/paths";
import {
  downloadCsvFile,
  listFiles,
  StoragePath,
  uploadCsvFile,
} from "util/storage";

const ANNOTATION_ID_PREFIX = "internal_";

export interface QuestionAnswerExample {
  local_id: number;
  query: string;
  answer: string;
  title: string;
  pred_rank: number;
  lower_query: string;
  lower_answer: string;
  lowerqa: string;
  claim_id: string;
  paper_id: string;
  doi: string;
}

export interface QuestionAnswerAnnotation {
  query: string;
  answer: string;
  title: string;
  correct_label: number | null;
  // Static for internal annotations
  case_id: string;
  origin: string;
  agreement: number;
  claim_id: string;
  paper_id: string;
}

export interface QuestionAnswer {
  example: QuestionAnswerExample;
  annotation: QuestionAnswerAnnotation;
}

function createDefaultAnnotation(
  example: QuestionAnswerExample,
  index: number
): QuestionAnswerAnnotation {
  return {
    query: `${example.query}`,
    answer: `${example.answer}`,
    title: `${example.title}`,
    correct_label: null,
    case_id: `${ANNOTATION_ID_PREFIX}${index}`,
    origin: `${ANNOTATION_ID_PREFIX}${index}`,
    agreement: -1,
    claim_id: example.claim_id,
    paper_id: example.paper_id,
  };
}

function sortAnnotationsById(
  a1: QuestionAnswerAnnotation,
  a2: QuestionAnswerAnnotation
): number {
  const id1 = parseInt(a1.case_id.slice(ANNOTATION_ID_PREFIX.length));
  const id2 = parseInt(a2.case_id.slice(ANNOTATION_ID_PREFIX.length));
  return id1 == id2 ? 0 : id1 > id2 ? 1 : -1;
}

export async function listToAnnotateFiles(): Promise<StoragePath[]> {
  return listFiles(QA_TO_ANNOTATE_BUCKET_PATH);
}

export async function listSearchTestingMetricFiles(): Promise<StoragePath[]> {
  return listFiles(QA_METRICS_BUCKET_PATH);
}

export type AnnotationsByQuery = { [query: string]: QuestionAnswer[] };

/** Downloads annotations from GCS and returns the data. */
export async function downloadAnnotationsByQuery(
  csvFileName: string,
  paperEval: boolean
): Promise<AnnotationsByQuery> {
  if (!csvFileName.endsWith(".csv")) {
    csvFileName = csvFileName + ".csv";
  }
  const examples =
    (await downloadCsvFile<QuestionAnswerExample>(
      csvFileName,
      paperEval ? QA_TO_ANNOTATE_PAPER_BUCKET_PATH : QA_TO_ANNOTATE_BUCKET_PATH
    )) || [];
  const annotations =
    (await downloadCsvFile<QuestionAnswerAnnotation>(
      csvFileName,
      paperEval ? QA_ANNOTATED_PAPER_BUCKET_PATH : QA_ANNOTATED_BUCKET_PATH
    )) || [];
  const annotationLookup: { [key: string]: QuestionAnswerAnnotation } = {};
  for (const annotation of annotations) {
    annotationLookup[annotation.answer] = annotation;
  }
  const annotationsByQuery: AnnotationsByQuery = {};
  for (let i = 0; i < examples.length; i++) {
    const example: QuestionAnswerExample = examples[i];
    if (!(example.answer in annotationLookup)) {
      annotationLookup[example.answer] = createDefaultAnnotation(example, i);
    }
    const annotation = annotationLookup[example.answer];
    if (!(example.query in annotationsByQuery)) {
      annotationsByQuery[annotation.query] = [];
    }
    annotationsByQuery[annotation.query].push({ example, annotation });
  }
  return annotationsByQuery;
}

/** Uploads annotations to GCS and returns the remote file name. */
export async function uploadCompletedAnnotations(
  csvFileName: string,
  paperEval: boolean,
  annotations: QuestionAnswerAnnotation[]
): Promise<string> {
  if (!csvFileName.endsWith(".csv")) {
    csvFileName = csvFileName + ".csv";
  }
  annotations.sort(sortAnnotationsById);
  return await uploadCsvFile(
    annotations,
    csvFileName,
    paperEval ? QA_ANNOTATED_PAPER_BUCKET_PATH : QA_ANNOTATED_BUCKET_PATH
  );
}
