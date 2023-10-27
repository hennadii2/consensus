import useLabels from "hooks/useLabels";
import React from "react";

export default function BetaFeatureTag() {
  const [betaLabels] = useLabels("beta");

  return (
    <div className="border-[#57AC91] text-base border  rounded-full text-[#57AC91] h-[27px] font-semibold items-center flex px-2.5">
      {betaLabels.feature}
    </div>
  );
}
