import Tooltip from "components/Tooltip";
import RigorousJournalTooltip from "components/Tooltip/RigorousJournalTooltip/RigorousJournalTooltip";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React from "react";

function VeryRigorousJournalTag() {
  const [pageLabels] = useLabels("tooltips.rigorous-journal");
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  return (
    <Tooltip interactive tooltipContent={<RigorousJournalTooltip value={10} />}>
      <div
        data-testid="very-rigorous-journal-tag"
        onClick={(e) => {
          if (isMobile) {
            e.preventDefault();
            e.stopPropagation();
          }
        }}
        className="text-sm justify-between font-bold whitespace-nowrap bg-white flex gap-1 border border-[#DEE0E3] rounded-md h-8 pl-2 pr-[6px] text-black items-center relative min-w-[181px]"
      >
        <img alt="Info" src="/icons/orange-search.svg" />
        <p>{pageLabels["very-tag"]}</p>
      </div>
    </Tooltip>
  );
}

export default VeryRigorousJournalTag;
