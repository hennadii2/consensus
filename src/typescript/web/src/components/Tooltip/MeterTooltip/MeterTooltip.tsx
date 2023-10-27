import BetaFeatureTag from "components/BetaTag/BetaFeatureTag";
import Button from "components/Button";
import Icon from "components/Icon";
import { WEB_URL_CONSENSUS_METER } from "constants/config";
import useLabels from "hooks/useLabels";
import React from "react";

interface MeterTooltipProps {}

/**
 * @component MeterTooltip
 * @description Tooltip for meter data
 * @example
 * return (
 *   <MeterTooltip />
 * )
 */
const MeterTooltip = ({}: MeterTooltipProps) => {
  const [tooltipsLabels] = useLabels("tooltips.meter");

  const title = tooltipsLabels.title;
  const content = tooltipsLabels.content;
  const buttonText = tooltipsLabels["learn-more"];
  const buttonUrl = WEB_URL_CONSENSUS_METER;
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
      <a
        onClick={handleClick}
        href={buttonUrl}
        target="__blank"
        rel="noreferrer"
      >
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

export default MeterTooltip;
