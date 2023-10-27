import Tooltip from "components/Tooltip";
import StudyTypeTooltip from "components/Tooltip/StudyTypeTooltip/StudyTypeTooltip";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React from "react";

interface AnimalTrialTagProps {
  pressable?: boolean;
}

function AnimalTrialTag(props?: AnimalTrialTagProps) {
  const [pageLabels] = useLabels("tooltips.animal-trial");
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  return (
    <Tooltip
      interactive
      maxWidth={306}
      tooltipContent={
        <StudyTypeTooltip
          title={pageLabels.title}
          content={pageLabels.content}
          icon="/icons/genetic-modification.svg"
          iconPyramid="bottom"
        />
      }
    >
      <div
        data-testid="animal-trial-tag"
        onClick={(e) => {
          if (isMobile && !props?.pressable) {
            e.preventDefault();
            e.stopPropagation();
          }
        }}
        className="text-sm justify-between font-bold whitespace-nowrap flex gap-1 border border-[#FF8A8A] rounded-md h-8 pl-2 pr-[6px] text-black items-center relative min-w-[115px]"
      >
        <img alt="Info" src="/icons/genetic-modification.svg" />
        <p>{pageLabels["tag"]}</p>
      </div>
    </Tooltip>
  );
}

export default AnimalTrialTag;
