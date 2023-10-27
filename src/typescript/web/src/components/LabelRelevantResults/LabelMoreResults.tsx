import Tooltip from "components/Tooltip";
import MoreResultsTooltip from "components/Tooltip/MoreResultsTooltip/MoreResultsTooltip";

const LabelMoreResults = () => {
  return (
    <div className="flex items-center gap-x-2 mb-4">
      <p className="text-base text-[#688092]">More results</p>
      <Tooltip
        interactive
        maxWidth={380}
        tooltipContent={<MoreResultsTooltip />}
      >
        <img
          className="min-w-[20px] max-w-[20px] h-5"
          alt="More result"
          src="/icons/info.svg"
        />
      </Tooltip>
    </div>
  );
};

export default LabelMoreResults;
