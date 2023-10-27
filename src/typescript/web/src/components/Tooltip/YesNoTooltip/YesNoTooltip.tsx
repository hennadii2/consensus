import useLabels from "hooks/useLabels";
import React from "react";

function YesNoTooltip() {
  const [pageLabels] = useLabels("screens.search");
  return (
    <div>
      <p className="text-lg font-bold">{pageLabels["try-yes-no-title"]}</p>
      <p className="text-base mt-1">{pageLabels["try-yes-no-desc"]}</p>
    </div>
  );
}

export default YesNoTooltip;
