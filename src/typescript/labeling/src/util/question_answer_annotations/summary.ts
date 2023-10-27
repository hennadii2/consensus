import { AnnotationsByQuery } from "util/question_answer_annotations/storage";

interface LabelCounts {
  labeled: number;
  unlabeled: number;
  total: number;
}

export interface AnnotationSummary {
  totalQueries: number;
  totalCounts: LabelCounts;
  perQuerySummary: { [query: string]: LabelCounts };
}

export function generateSummary(
  annotationsByQuery: AnnotationsByQuery
): AnnotationSummary {
  let totalLabeled = 0;
  let totalUnlabeled = 0;
  const perQuerySummary: { [query: string]: LabelCounts } = {};
  for (const query of Object.keys(annotationsByQuery)) {
    const annotations = annotationsByQuery[query];
    const labeled = annotations.filter(
      (x) => x.annotation.correct_label !== null
    ).length;
    const unlabeled = annotations.length - labeled;
    totalLabeled += labeled;
    totalUnlabeled += unlabeled;
    perQuerySummary[query] = {
      total: annotations.length,
      labeled,
      unlabeled,
    };
  }
  return {
    totalQueries: Object.keys(annotationsByQuery).length,
    totalCounts: {
      total: totalLabeled + totalUnlabeled,
      labeled: totalLabeled,
      unlabeled: totalUnlabeled,
    },
    perQuerySummary,
  };
}
