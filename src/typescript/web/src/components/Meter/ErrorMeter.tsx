import useLabels from "hooks/useLabels";
import React from "react";

interface ErrorProps {
  message?: string;
}

function ErrorMeter({ message }: ErrorProps) {
  const [meterLabels] = useLabels("meter");

  return (
    <div className="text-sm flex flex-col gap-y-4 bg-[#F8E7E7] text-[#364B44] rounded-lg p-4">
      <p>
        <strong>{meterLabels["error-title"]}</strong>
      </p>
      <p>{message || meterLabels["error-desc"]}</p>
    </div>
  );
}

export default ErrorMeter;
