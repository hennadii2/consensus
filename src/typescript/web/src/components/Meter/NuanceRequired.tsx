import useLabels from "hooks/useLabels";
import React from "react";

function NuanceRequired() {
  const [meterLabels] = useLabels("meter");

  return (
    <div className="text-sm flex flex-col gap-y-4 bg-[#F1F4F6] text-[#364B44] rounded-lg p-4">
      <p>
        <strong>{meterLabels["can-not-synthesize"]["title"]}</strong>{" "}
        {meterLabels["can-not-synthesize"]["desc"]}
      </p>
    </div>
  );
}

export default NuanceRequired;
