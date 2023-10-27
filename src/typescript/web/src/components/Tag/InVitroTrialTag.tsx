import Tooltip from "components/Tooltip";
import StudyTypeTooltip from "components/Tooltip/StudyTypeTooltip/StudyTypeTooltip";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React from "react";

interface InVitroTrialTagProps {
  pressable?: boolean;
}

function InVitroTrialTag(props?: InVitroTrialTagProps) {
  const [pageLabels] = useLabels("tooltips.in-vitro-trial");
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  return (
    <Tooltip
      interactive
      maxWidth={306}
      tooltipContent={
        <StudyTypeTooltip
          title={pageLabels.title}
          content={pageLabels.content}
          icon="/icons/bacteria.svg"
          iconPyramid="bottom"
        />
      }
    >
      <div
        data-testid="in-vitro-trial-tag"
        onClick={(e) => {
          if (isMobile && !props?.pressable) {
            e.preventDefault();
            e.stopPropagation();
          }
        }}
        className="text-sm justify-between font-bold whitespace-nowrap flex gap-1 border border-[#FF8A8A] rounded-md h-9 pl-2 pr-[6px] text-black items-center relative min-w-[117px]"
      >
        <img alt="Info" src="/icons/bacteria.svg" />
        <p>{pageLabels["tag"]}</p>
      </div>
    </Tooltip>
  );
}

export default InVitroTrialTag;
