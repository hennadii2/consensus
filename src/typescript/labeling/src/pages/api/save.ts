import type { NextApiRequest, NextApiResponse } from "next";
import {
  QuestionAnswerAnnotation,
  uploadCompletedAnnotations,
} from "util/question_answer_annotations/storage";

interface SaveRequest extends NextApiRequest {
  body: {
    csvFile: string;
    paperEval: boolean;
    annotations: QuestionAnswerAnnotation[];
  };
}

export default async function handler(req: SaveRequest, res: NextApiResponse) {
  const { csvFile, paperEval, annotations } = req.body;
  await uploadCompletedAnnotations(csvFile, paperEval, annotations);
  res.status(200).json({});
}
