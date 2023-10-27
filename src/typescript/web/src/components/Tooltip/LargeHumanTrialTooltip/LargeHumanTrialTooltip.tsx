import useLabels from "hooks/useLabels";
import React from "react";

/**
 * @component LargeHumanTrialTooltip
 * @description Tooltip for large human trial
 * @example
 * return (
 *   <LargeHumanTrialTooltip />
 * )
 */

const LargeHumanTrialTooltip = () => {
  const [pageLabels] = useLabels("tooltips.large-human-trial");
  return (
    <div className="flex flex-col text-black">
      <p className="font-bold mb-3 text-lg flex items-center">
        <img className="w-6 h-6 mr-3" alt="Info" src="/icons/people.svg" />
        {pageLabels.title}
      </p>
      <div className="flex flex-col text-base space-y-2">
        <p>{pageLabels.content[0]}</p>
        <div>
          <div className="flex flex-row space-x-2">
            <img
              src={"/icons/check-mark.svg"}
              className="w-4 h-4 mt-1"
              alt="Check icon"
            />
            <p>{pageLabels.content[1]}</p>
          </div>
          <div className="flex flex-row space-x-2">
            <img
              src={"/icons/check-mark.svg"}
              className="w-4 h-4 mt-1"
              alt="Check icon"
            />
            <p>{pageLabels.content[2]}</p>
          </div>
          <div className="flex flex-row space-x-2">
            <img
              src={"/icons/check-mark.svg"}
              className="w-4 h-4 mt-1"
              alt="Check icon"
            />
            <p>{pageLabels.content[3]}</p>
          </div>
        </div>
        <p>{pageLabels.content[4]}</p>
      </div>
    </div>
  );
};

export default LargeHumanTrialTooltip;
