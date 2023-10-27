import Tooltip from "components/Tooltip";
import StudyTypeTooltip from "components/Tooltip/StudyTypeTooltip/StudyTypeTooltip";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React from "react";

interface LiteratureReviewTagProps {
  pressable?: boolean;
}

function LiteratureReviewTag(props?: LiteratureReviewTagProps) {
  const [pageLabels] = useLabels("tooltips.literature-review");
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  return (
    <Tooltip
      interactive
      maxWidth={306}
      tooltipContent={
        <StudyTypeTooltip
          title={pageLabels.title}
          content={pageLabels.content}
          icon="/icons/open-book.svg"
          iconPyramid="middle"
        />
      }
    >
      <div
        data-testid="literature-review-tag"
        onClick={(e) => {
          if (isMobile && !props?.pressable) {
            e.preventDefault();
            e.stopPropagation();
          }
        }}
        className="text-sm justify-between font-bold whitespace-nowrap flex gap-1 border border-[#FCBA13] rounded-md h-8 pl-2 pr-[6px] text-black items-center relative min-w-[154px]"
      >
        <img alt="Info" src="/icons/open-book.svg" />
        <p>{pageLabels["tag"]}</p>
      </div>
    </Tooltip>
  );
}

export default LiteratureReviewTag;
