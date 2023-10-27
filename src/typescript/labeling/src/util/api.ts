import { QuestionAnswerAnnotation } from "util/question_answer_annotations/storage";

export async function saveQaAnnotations(
  csvFile: string,
  paperEval: boolean,
  annotations: QuestionAnswerAnnotation[]
): Promise<void> {
  await fetch("/api/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ csvFile: csvFile, paperEval, annotations }),
  });
}
