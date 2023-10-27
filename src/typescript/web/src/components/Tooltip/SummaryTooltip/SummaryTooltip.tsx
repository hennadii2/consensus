import BetaFeatureTag from "components/BetaTag/BetaFeatureTag";
import Button from "components/Button";
import Icon from "components/Icon";
import { SUMMARY_TOOL_TIP } from "constants/config";
import useLabels from "hooks/useLabels";
import React from "react";

interface SummaryTooltipProps {}

/**
 * @component SummaryTooltip
 * @description Tooltip for meter data
 * @example
 * return (
 *   <SummaryTooltip />
 * )
 */
const SummaryTooltip = ({}: SummaryTooltipProps) => {
  const [tooltipsLabels] = useLabels("tooltips.summary");

  const title = tooltipsLabels.title;
  const content = tooltipsLabels.content;
  const buttonText = tooltipsLabels["learn-more"];
  const buttonUrl = SUMMARY_TOOL_TIP;
  const handleClick = (e: any) => {
    e.preventDefault();
    window.open(buttonUrl);
  };

  return (
    <div data-testid="tooltip-score" className="text-[#364B44]">
      <div className="flex justify-between">
        <p className="font-bold mb-3 text-lg flex items-center">{title}</p>
        <BetaFeatureTag />
      </div>
      <p
        className="text-base"
        dangerouslySetInnerHTML={{ __html: content }}
      ></p>
      <div className="p-4 rounded-md bg-red-100 text-[#364B44] flex mt-4">
        <div className="mr-2">
          <img
            className="min-w-[18px] max-w-[18px]"
            alt="Info"
            src="/icons/warning-meter.svg"
          />
        </div>
        <div
          className="font-semibold"
          dangerouslySetInnerHTML={{ __html: tooltipsLabels.warning }}
        ></div>
      </div>
      <a onClick={handleClick} target="__blank" rel="noreferrer">
        <Button className="bg-gray-300 px-4 py-2 flex items-center rounded-full mt-4 font-medium text-[#000000]">
          {buttonText}
          <Icon
            name="external-link"
            size={16}
            className="ml-4 text-[#889CAA]"
          />
        </Button>
      </a>
    </div>
  );
};

export default SummaryTooltip;
