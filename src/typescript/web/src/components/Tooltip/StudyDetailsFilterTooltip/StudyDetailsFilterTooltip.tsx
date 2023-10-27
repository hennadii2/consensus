import useLabels from "hooks/useLabels";
import React from "react";

/**
 * @component StudyDetailsFilterTooltip
 * @description Tooltip for case study
 * @example
 * return (
 *   <StudyDetailsFilterTooltip />
 * )
 */
const StudyDetailsFilterTooltip = () => {
  const [tooltipsLabels] = useLabels("tooltips.study-details-filter");

  return (
    <div className="text-black" data-testid="tooltip-study-details-filter">
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
        className="text-base mb-4"
        dangerouslySetInnerHTML={{ __html: tooltipsLabels["content"] }}
      ></p>

      <p className="text-gray-550 italic text-base">
        {tooltipsLabels["footer"]}
      </p>
    </div>
  );
};

export default StudyDetailsFilterTooltip;
