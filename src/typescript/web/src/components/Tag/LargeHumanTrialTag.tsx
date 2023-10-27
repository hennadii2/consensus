import Tooltip from "components/Tooltip";
import LargeHumanTrialTooltip from "components/Tooltip/LargeHumanTrialTooltip/LargeHumanTrialTooltip";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React from "react";

interface LargeHumanTrialTagProps {
  isDetail?: boolean;
}

function LargeHumanTrialTag({ isDetail }: LargeHumanTrialTagProps) {
  const [pageLabels] = useLabels("tooltips.large-human-trial");
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  return (
    <Tooltip
      interactive
      maxWidth={334}
      tooltipContent={<LargeHumanTrialTooltip />}
    >
      <div
        data-testid="large-human-trial-tag"
        onClick={(e) => {
          if (isMobile) {
            e.preventDefault();
            e.stopPropagation();
          }
        }}
        className="text-sm bg-white whitespace-nowrap font-bold flex gap-1 border border-[#5CBAFF] rounded-md h-8 pl-2 pr-[6px] text-black items-center relative min-w-[156px]"
      >
        <img alt="Info" src="/icons/people.svg" />
        <p>{pageLabels["tag"]}</p>
      </div>
    </Tooltip>
  );
}

export default LargeHumanTrialTag;
