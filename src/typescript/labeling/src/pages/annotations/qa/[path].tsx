import CheckBox from "components/CheckBox";
import QuestionAnswerAnnotationCard from "components/QuestionAnswerAnnotation";
import SaveButton from "components/SaveButton";
import { GetServerSidePropsContext } from "next";
import { useState } from "react";
import { saveQaAnnotations } from "util/api";
import {
  AnnotationsByQuery,
  downloadAnnotationsByQuery,
  QuestionAnswerAnnotation,
} from "util/question_answer_annotations/storage";
import {
  AnnotationSummary,
  generateSummary,
} from "util/question_answer_annotations/summary";

const QA_ANNOTATION_INSTRUCTIONS =
  "Assign a label [1-3] for how well the sentence answers or relates to the question or topic listed on the top of each card. 1 = good answer, 2 = ok answer, 3 = bad answer";
const QA_PAPER_ANNOTATION_INSTRUCTIONS =
  "Assign a label [0-4] for how relevant the paper title and abstract to the query. 4 = perfectly relevant, 3 = relevant, 2 = partially relevant, 1 = tangentially relevant, 0 = irrelevant";

interface QuestionAnswerAnnotationsProps {
  csvFile: string;
  paperEval: boolean;
  annotationsByQuery: AnnotationsByQuery;
}

const QuestionAnswerAnnotations = (props: QuestionAnswerAnnotationsProps) => {
  const [data, setData] = useState<AnnotationsByQuery>(
    props.annotationsByQuery
  );
  const [changedSinceLastSave, setChangedSinceLastSave] =
    useState<boolean>(false);
  const [hideLabeled, setHideLabeled] = useState<boolean>(false);
  const [summary, setSummary] = useState<AnnotationSummary>(
    generateSummary(data)
  );

  const handleOnLabelUpdated = (
    label: number,
    query: string,
    index: number
  ) => {
    const updatedData = data;
    updatedData[query][index].annotation.correct_label = label;
    setData(updatedData);
    setSummary(generateSummary(updatedData));
    setChangedSinceLastSave(true);
  };

  const handleOnSave = async () => {
    // Reduce down to set of completed annotations then save
    const sortedQueries = Object.keys(data).sort();
    let annotations: QuestionAnswerAnnotation[] = [];
    for (const query of sortedQueries) {
      const completed = data[query]
        .filter((x) => x.annotation.correct_label !== null)
        .map((x) => x.annotation);
      annotations = [...annotations, ...completed];
    }
    await saveQaAnnotations(props.csvFile, props.paperEval, annotations);
    setChangedSinceLastSave(false);
  };

  return (
    <div>
      <div className="flex flex-col p-5 space-y-2 sticky top-0 bg-gray-100">
        <div className="flex flex-row">
          <h1 className="flex-none">{`${props.csvFile}`}</h1>
          <div className="flex-auto"></div>
          <SaveButton
            onSave={handleOnSave}
            autoSave={false}
            needsSave={changedSinceLastSave}
          />
        </div>
        <div className="flex flex-row space-x-2">
          <div>{`${summary.totalQueries} Queries`}</div>
          <div>
            {`Labeled: ${summary.totalCounts.labeled} / ${summary.totalCounts.total}`}
          </div>
        </div>
        <CheckBox
          label="Hide Labeled"
          isChecked={hideLabeled}
          onChange={() => setHideLabeled(!hideLabeled)}
        />
        <h1 className="pt-5 text-gray-600">{QA_ANNOTATION_INSTRUCTIONS}</h1>
      </div>
      <div>
        {Object.keys(data)
          .sort()
          .map((query, queryIndex) => {
            const querySummary = summary.perQuerySummary[query];
            return (
              <div
                key={`query-${queryIndex}`}
                className="flex flex-col m-2 rounded-2xl border-2 border-gray-200"
              >
                <h1 className="text-gray-500 p-3">
                  {`${query}: ${querySummary.labeled}/${querySummary.total}`}
                </h1>
                <div>
                  {data[query].map((item, index) => {
                    const isLabeled = item.annotation.correct_label !== null;
                    return isLabeled && hideLabeled ? (
                      <></>
                    ) : (
                      <QuestionAnswerAnnotationCard
                        key={`answer-${query}-${index}`}
                        index={index}
                        label={item.annotation.correct_label}
                        query={item.annotation.query}
                        answer={item.annotation.answer}
                        onLabelUpdated={handleOnLabelUpdated}
                        title={item.annotation.title}
                        doi={item.example.doi}
                        paperEval={props.paperEval}
                      />
                    );
                  })}
                </div>
              </div>
            );
          })}
      </div>
    </div>
  );
};

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const fileName = context.query.path?.toString() || "";
  const paperEval = context.query.paperEval?.toString()  === "true";
  const annotationsByQuery = await downloadAnnotationsByQuery(fileName, paperEval);
  return {
    props: {
      csvFile: fileName,
      paperEval: paperEval,
      annotationsByQuery,
    },
  };
}

export default QuestionAnswerAnnotations;
