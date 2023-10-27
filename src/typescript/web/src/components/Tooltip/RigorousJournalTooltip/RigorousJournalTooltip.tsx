import useLabels from "hooks/useLabels";
import React from "react";

const SCISCORE_URL = "https://www.sciscore.com/rti/overview.php";

interface PoweredBySciScoreProps {
  size?: "medium" | "small";
}

export const PoweredBySciScore = ({ size }: PoweredBySciScoreProps) => {
  const [componentLabels] = useLabels("tooltips.rigorous-journal");

  return (
    <div
      className={`flex gap-2  items-center text-[#889CAA] whitespace-nowrap ${
        size === "small" ? "text-xs" : "text-base"
      }`}
    >
      {componentLabels["powered-by"]}
      <img
        alt="SciScore"
        className={`${size === "small" ? "h-3" : "h-4"}`}
        src="/images/sciscore-logo.webp"
      />
    </div>
  );
};

/**
 * @component RigorousJournalTooltip
 * @description Tooltip for score
 * @example
 * return (
 *   <RigorousJournalTooltip value={20} />
 * )
 */

interface RigorousJournalTooltipProps {
  value: number;
  instance?: any;
}

const RigorousJournalTooltip = ({
  value,
  instance,
}: RigorousJournalTooltipProps) => {
  const [generalLabels, componentLabels] = useLabels(
    "general",
    "tooltips.rigorous-journal"
  );

  const handleClick = (e: any) => {
    e.preventDefault();
    window.open(SCISCORE_URL);
  };

  return (
    <div className="overflow-hidden">
      <div className="bg-[#F3F8FB] absolute w-full left-0 top-0 rounded-t-xl">
        <div className="px-4 py-3 relative">
          <PoweredBySciScore />
        </div>
      </div>

      <p
        dangerouslySetInnerHTML={{
          __html: componentLabels["title"].replace("{value}", value),
        }}
        className="text-base mb-1 mt-10"
      />
      <p
        dangerouslySetInnerHTML={{
          __html: componentLabels["content"],
        }}
        className="text-base"
      />
      <a
        onClick={handleClick}
        href={SCISCORE_URL}
        target="__blank"
        rel="noreferrer"
        className="text-[#222F2B] cursor-pointer border-[#DEE0E3] border px-4 h-[36px] rounded-full mt-3 flex-row justify-between items-center flex"
      >
        <div className="flex flex-row items-center">
          <span className="text-base">Learn more</span>
        </div>
        <img
          className="w-5 h-5"
          alt="External Link"
          src="/icons/external-link.svg"
        />
      </a>
    </div>
  );
};

export default RigorousJournalTooltip;
