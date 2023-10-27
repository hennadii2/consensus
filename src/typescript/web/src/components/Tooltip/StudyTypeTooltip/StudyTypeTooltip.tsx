import { HIERARCHY_OF_EVIDENCE_URL } from "constants/config";
import useLabels from "hooks/useLabels";
import React from "react";

interface StudyTypeTooltipProps {
  title: string;
  content: string;
  icon: string;
  iconPyramid?: "top" | "middle" | "bottom";
  showLink?: boolean;
}

/**
 * @component StudyTypeTooltip
 * @description Tooltip for case study
 * @example
 * return (
 *   <StudyTypeTooltip />
 * )
 */
const StudyTypeTooltip = ({
  title,
  icon,
  content,
  iconPyramid,
  showLink = true,
}: StudyTypeTooltipProps) => {
  const [tooltipsLabels] = useLabels("tooltips");

  return (
    <div data-testid="tooltip-score">
      <p className="font-bold mb-3 text-lg flex items-center">
        <img className="w-6 mr-2" alt={title} src={icon} />
        {title}
      </p>
      <p
        className="text-base"
        dangerouslySetInnerHTML={{ __html: content }}
      ></p>
      {showLink ? (
        <div
          onClick={(e) => {
            window.open(HIERARCHY_OF_EVIDENCE_URL, "_blank");
            e.preventDefault();
          }}
          className="text-[#222F2B] cursor-pointer border-[#DEE0E3] border px-4 h-[36px] rounded-full mt-3 flex-row justify-between items-center flex"
        >
          <div className="flex flex-row items-center">
            {iconPyramid ? (
              <img
                className="w-5 h-5 mr-3"
                alt="Pyramid"
                src={
                  iconPyramid === "top"
                    ? "/images/pyramid1.svg"
                    : iconPyramid === "middle"
                    ? "/images/pyramid2.svg"
                    : "/images/pyramid3.svg"
                }
              />
            ) : null}
            <span className="text-base">Learn more</span>
          </div>
          <img
            className="w-5 h-5"
            alt="External Link"
            src="/icons/external-link.svg"
          />
        </div>
      ) : null}
    </div>
  );
};

export default StudyTypeTooltip;
