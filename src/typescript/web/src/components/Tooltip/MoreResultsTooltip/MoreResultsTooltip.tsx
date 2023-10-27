import useLabels from "hooks/useLabels";
import React from "react";

interface MoreResultsTooltipProps {}

/**
 * @component MoreResultsTooltip
 * @description Tooltip for more results
 * @example
 * return (
 *   <MoreResultsTooltip />
 * )
 */
const MoreResultsTooltip = ({}: MoreResultsTooltipProps) => {
  const [tooltipsLabels] = useLabels("tooltips.more-results");

  const title = tooltipsLabels.title;
  const content = tooltipsLabels.content;

  return (
    <div className="text-[#364B44]">
      <div className="flex justify-between">
        <p className="font-bold mb-3 text-lg flex items-center">{title}</p>
      </div>
      <p
        className="text-base"
        dangerouslySetInnerHTML={{ __html: content }}
      ></p>
    </div>
  );
};

export default MoreResultsTooltip;
