import Tooltip from "components/Tooltip";
import StudyTypeTooltip from "components/Tooltip/StudyTypeTooltip/StudyTypeTooltip";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React from "react";

interface CaseStudyTagProps {
  pressable?: boolean;
}

function CaseStudyTag(props?: CaseStudyTagProps) {
  const [pageLabels] = useLabels("tooltips.case-study");
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  return (
    <Tooltip
      interactive
      maxWidth={306}
      tooltipContent={
        <StudyTypeTooltip
          title={pageLabels.title}
          content={pageLabels.content}
          icon="/icons/personal-information.svg"
          iconPyramid="bottom"
        />
      }
    >
      <div
        data-testid="case-study-tag"
        onClick={(e) => {
          if (isMobile && !props?.pressable) {
            e.preventDefault();
            e.stopPropagation();
          }
        }}
        className="text-sm justify-between font-bold whitespace-nowrap flex gap-1 border border-[#FF8A8A] rounded-md h-8 pl-2 pr-[6px] text-black items-center relative min-w-[119px]"
      >
        <img alt="Info" src="/icons/personal-information.svg" />
        <p>{pageLabels["tag"]}</p>
      </div>
    </Tooltip>
  );
}

export default CaseStudyTag;
