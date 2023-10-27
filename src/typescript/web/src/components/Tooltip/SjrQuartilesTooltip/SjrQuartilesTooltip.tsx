import useLabels from "hooks/useLabels";
import React from "react";

/**
 * @component SjrQuartilesTooltip
 * @description Tooltip for case study
 * @example
 * return (
 *   <SjrQuartilesTooltip />
 * )
 */
const SjrQuartilesTooltip = () => {
  const [tooltipsLabels] = useLabels("tooltips.sjr-quartiles");

  return (
    <div className="text-[#364B44]" data-testid="tooltip-sjr-quartiles">
      <p className="font-bold mb-3 text-lg flex items-center">
        {tooltipsLabels["title"]}
      </p>
      <div className="flex flex-row gap-x-1 mb-3">
        <div className="w-5 h-2 rounded-full bg-[#FFB800]" />
        <div className="w-5 h-2 rounded-full bg-[#FFB800]" />
        <div className="w-5 h-2 rounded-full bg-[#D9D9D9]" />
        <div className="w-5 h-2 rounded-full bg-[#D9D9D9]" />
      </div>
      <p
        className="text-base mb-3"
        dangerouslySetInnerHTML={{ __html: tooltipsLabels["content"] }}
      ></p>
      <p className="text-[#688092] italic text-base">
        {tooltipsLabels["footer"]}
      </p>
    </div>
  );
};

export default SjrQuartilesTooltip;
