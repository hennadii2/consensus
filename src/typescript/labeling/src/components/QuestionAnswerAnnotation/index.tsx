import { useState } from "react";
import AnnotationButton from "./AnnotationButton";

type QuestionAnswerAnnotationCardProps = {
  index: number;
  label: number | null;
  query: string;
  answer: string;
  title: string;
  doi: string;
  paperEval: boolean;
  onLabelUpdated: (label: number, query: string, index: number) => void;
};

const QuestionAnswerAnnotationCard = (
  props: QuestionAnswerAnnotationCardProps
) => {
  const [selectedLabel, setSelectedLabel] = useState<number | null>(
    props.label
  );

  const onAnnotationButtonClick = (label: number) => {
    props.onLabelUpdated(label, props.query, props.index);
    setSelectedLabel(label);
  };

  const doi_link = "https://doi.org/" + props.doi;

  /**
   * Temporary workaround for transitioning from Claims to Paper eval
   * Paper eval has 5 labels, 4-0, in descending order
   * Claims eval has 3 labels, 1-3, in ascending order
   */
  const getAnnotationButtons = (paperEval: boolean) => {
    if (paperEval) {
      return (
        <>
          <AnnotationButton
            label={4}
            color={"green"}
            isSelected={selectedLabel == 4}
            onClick={onAnnotationButtonClick}
          ></AnnotationButton>
          <AnnotationButton
            label={3}
            color={"lime"}
            isSelected={selectedLabel == 3}
            onClick={onAnnotationButtonClick}
          ></AnnotationButton>
          <AnnotationButton
            label={2}
            color={"yellow"}
            isSelected={selectedLabel == 2}
            onClick={onAnnotationButtonClick}
          ></AnnotationButton>
          <AnnotationButton
            label={1}
            color={"orange"}
            isSelected={selectedLabel == 1}
            onClick={onAnnotationButtonClick}
          ></AnnotationButton>
          <AnnotationButton
            label={0}
            color={"red"}
            isSelected={selectedLabel == 0}
            onClick={onAnnotationButtonClick}
          ></AnnotationButton>
        </>
      );
    } else {
      return (
        <>
          <AnnotationButton
            label={1}
            color={"green"}
            isSelected={selectedLabel == 1}
            onClick={onAnnotationButtonClick}
          ></AnnotationButton>
          <AnnotationButton
            label={2}
            color={"yellow"}
            isSelected={selectedLabel == 2}
            onClick={onAnnotationButtonClick}
          ></AnnotationButton>
          <AnnotationButton
            label={3}
            color={"red"}
            isSelected={selectedLabel == 3}
            onClick={onAnnotationButtonClick}
          ></AnnotationButton>
        </>
      );
    }
  }

  return (
    <div className="flex flex-col rounded-2xl border-1 border-gray-600 bg-gray-100 p-3 m-2">
      <h1 className="text-gray-500 pb-2">{`${props.index}: ${props.query}`}</h1>
      <div className="flex bg-white p-2">
        <div className="flex space-x-2 items-center">
          {getAnnotationButtons(props.paperEval)}
        </div>
        <div className="pl-4 flex justify-center">
          <div className="flex items-center">{props.answer}</div>
        </div>
      </div>
      {props.title ?
        <div className="pl-4 flex justify-left">
          <div className="flex items-center"><b>Title: </b>{props.title}</div>
        </div>
        : null}
      {props.doi ?
        <div className="pl-4 flex justify-left">
          <div className="flex items-center">
            <a target="_blank" rel="noreferrer" className="text-blue-600" href={doi_link}>DOI</a>
          </div>
        </div>
        : null}
    </div>
  );
};

export default QuestionAnswerAnnotationCard;
