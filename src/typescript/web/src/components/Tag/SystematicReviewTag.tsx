import Tooltip from "components/Tooltip";
import StudyTypeTooltip from "components/Tooltip/StudyTypeTooltip/StudyTypeTooltip";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React from "react";

interface SystematicReviewTagProps {
  pressable?: boolean;
}

function SystematicReviewTag(props?: SystematicReviewTagProps) {
  const [pageLabels] = useLabels("tooltips.systematic-review");
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  return (
    <Tooltip
      interactive
      maxWidth={306}
      tooltipContent={
        <StudyTypeTooltip
          title={pageLabels.title}
          content={pageLabels.content}
          icon="/icons/folder.svg"
          iconPyramid="top"
        />
      }
    >
      <div
        data-testid="systematic-review-tag"
        onClick={(e) => {
          if (isMobile && !props?.pressable) {
            e.preventDefault();
            e.stopPropagation();
          }
        }}
        className="text-sm justify-between font-bold whitespace-nowrap flex gap-1 border border-[#5AD3AB] rounded-md h-8 pl-2 pr-[6px] text-black items-center relative min-w-[162px]"
      >
        <img alt="Info" src="/icons/folder.svg" />
        <p>{pageLabels["tag"]}</p>
      </div>
    </Tooltip>
  );
}

export default SystematicReviewTag;
