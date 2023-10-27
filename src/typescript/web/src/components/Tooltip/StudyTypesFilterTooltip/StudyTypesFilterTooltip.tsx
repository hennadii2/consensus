import { HIERARCHY_OF_EVIDENCE_URL } from "constants/config";
import useLabels from "hooks/useLabels";
import React from "react";

/**
 * @component StudyTypesFilterTooltip
 * @description Tooltip for case study
 * @example
 * return (
 *   <StudyTypesFilterTooltip />
 * )
 */
const StudyTypesFilterTooltip = () => {
  const [tooltipsLabels] = useLabels("tooltips.study-types");

  return (
    <div className="text-[#364B44]" data-testid="tooltip-study-types-filter">
      <div className="flex flex-row items-center gap-x-[6px] mb-3">
        <img
          className="min-w-[24px] max-w-[24px] h-6 w-6 ml-1 mr-[6px]"
          alt="Sparkler"
          src="/icons/sparkler.svg"
        />
        <p className="font-bold text-lg flex items-center">
          {tooltipsLabels["title"]}
        </p>
      </div>
      <p
        className="text-base mb-3"
        dangerouslySetInnerHTML={{
          __html: tooltipsLabels["content"].replace(
            "HIERARCHY_OF_EVIDENCE_URL",
            HIERARCHY_OF_EVIDENCE_URL
          ),
        }}
      ></p>
      <p className="text-[#688092] italic text-base">
        {tooltipsLabels["footer"]}
      </p>
      <div className="flex flex-row mt-5">
        <img
          className="min-w-[70px] max-w-[70px] h-[70px] w-[70px] ml-1 mr-[27px] z-10"
          alt="Pyramid"
          src="/images/pyramid.svg"
        />
        <div className="flex flex-col gap-y-1">
          <div className="flex flex-row h-[21px] items-center">
            <div className="h-[1px] w-[62px] bg-[#D9D9D9] absolute -ml-[62px]" />
            <div className="h-[10px] w-[10px] rounded-full bg-[#46A759] mr-[6px]" />
            <span className="text-xs text-[#688092]">
              Green indicates strong evidence
            </span>
          </div>
          <div className="flex flex-row h-[21px] items-center">
            <div className="h-[1px] w-[62px] bg-[#D9D9D9] absolute -ml-[62px]" />
            <div className="h-[10px] w-[10px] rounded-full bg-[#FFB800] mr-[6px]" />
            <span className="text-xs text-[#688092]">
              Yellow indicates medium evidence
            </span>
          </div>
          <div className="flex flex-row h-[21px] items-center">
            <div className="h-[1px] w-[62px] bg-[#D9D9D9] absolute -ml-[62px]" />
            <div className="h-[10px] w-[10px] rounded-full bg-[#E3504F] mr-[6px]" />
            <span className="text-xs text-[#688092]">
              Red indicates weak evidence
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudyTypesFilterTooltip;
