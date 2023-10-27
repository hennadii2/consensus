import Tooltip from "components/Tooltip";
import DisputedPaperTooltip from "components/Tooltip/DisputedPaperTooltip/DisputedPaperTooltip";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React from "react";

interface DisputedPaperTagProps {
  reason?: string;
  url?: string;
  tooltip?: string;
}

function DisputedPaperTag({ reason, url, tooltip }: DisputedPaperTagProps) {
  const [pageLabels] = useLabels("tooltips.disputed");
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  return (
    <div
      data-testid="disputed-paper-tag"
      onClick={(e) => {
        if (isMobile) {
          e.preventDefault();
          e.stopPropagation();
        }
      }}
      className="text-sm justify-between bg-[#FFDBDB] font-bold whitespace-nowrap flex gap-1 border border-[#DEE0E3] rounded-md h-[28px] pl-2 pr-[6px] text-[#364B44] items-center relative min-w-[126px]"
    >
      <img alt="Info" src="/icons/disputed.svg" />
      <p>{pageLabels["tag"]}</p>
      {reason && url ? (
        <Tooltip
          interactive
          maxWidth={306}
          tooltipContent={
            <DisputedPaperTooltip
              title={pageLabels.title}
              content={pageLabels.content.replace("{reason}", reason)}
              icon="/icons/disputed.svg"
              buttonText={pageLabels.button}
              buttonUrl={url}
            />
          }
        >
          <img
            className="min-w-[16px] max-w-[16px] h-4"
            alt="Info"
            src="/icons/info.svg"
          />
        </Tooltip>
      ) : tooltip ? (
        <Tooltip
          interactive
          tooltipContent={
            <div>
              <p className="text-base">{tooltip}</p>
            </div>
          }
        >
          <img
            className="min-w-[16px] max-w-[16px] h-4"
            alt="Info"
            src="/icons/info.svg"
          />
        </Tooltip>
      ) : null}
    </div>
  );
}

export default DisputedPaperTag;
