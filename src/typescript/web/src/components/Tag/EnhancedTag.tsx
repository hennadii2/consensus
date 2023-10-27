import Tooltip from "components/Tooltip";
import useLabels from "hooks/useLabels";

interface EnhancedTagProps {
  enhanced?: boolean;
  isDetail?: boolean;
}

function EnhancedTag({ enhanced, isDetail }: EnhancedTagProps) {
  const [detailsLabels, componentLabels] = useLabels(
    "screens.details",
    "tooltips.enhanced"
  );
  if (enhanced) {
    return (
      <Tooltip tooltipContent={<p>{componentLabels.content}</p>}>
        {isDetail ? (
          <div
            style={{
              background:
                "linear-gradient(86.47deg, #0FAAD9 -145.17%, #51C5CA 241.67%)",
            }}
            className="cursor-pointer sm:cursor-default flex flex-row items-center space-x-2 h-7 rounded-md px-2"
          >
            <img
              alt="enhanced"
              src="/icons/enhanced-detail.svg"
              className="w-4 h-4"
            />
            <p className="text-white font-bold text-sm">
              {detailsLabels.enhanced}
            </p>
            <img
              alt="info-white"
              src="/icons/info-white.svg"
              className="w-3 h-3"
            />
          </div>
        ) : (
          <div data-testid="enhanced-indicator" className="w-6 h-6">
            <img
              id="enhanced-indicator-element"
              alt="enhanced"
              src="/icons/enhanced.svg"
              className="w-6 h-6"
            />
          </div>
        )}
      </Tooltip>
    );
  }

  return null;
}

export default EnhancedTag;
