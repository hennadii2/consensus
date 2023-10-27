import Tooltip from "components/Tooltip";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React from "react";

interface HightlyCitiedTagProps {
  isDetail?: boolean;
}

function HightlyCitiedTag({ isDetail }: HightlyCitiedTagProps) {
  const [pageLabels] = useLabels("tooltips.highly-cited");
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  return (
    <Tooltip
      tooltipContent={
        <div>
          <p className="font-bold mb-3 text-lg flex items-center">
            <img className="w-6 mr-2" alt="Quote" src="/icons/quote.svg" />
            {pageLabels["tag"]}
          </p>
          <p className="text-lg font-bold">
            {isDetail ? pageLabels["title"] : pageLabels["result-title"]}
          </p>
          <p className="text-base mt-1">{pageLabels["content"]}</p>
        </div>
      }
    >
      <div
        data-testid="highly-cited-tag"
        onClick={(e) => {
          if (isMobile) {
            e.preventDefault();
            e.stopPropagation();
          }
        }}
        className="text-sm bg-white whitespace-nowrap font-bold flex gap-1 border border-[#DEE0E3] rounded-md h-8 pl-2 pr-[6px] text-black items-center relative min-w-[119px]"
      >
        <img alt="Info" src="/icons/quote.svg" />
        <p>{pageLabels["tag"]}</p>
      </div>
    </Tooltip>
  );
}

export default HightlyCitiedTag;
