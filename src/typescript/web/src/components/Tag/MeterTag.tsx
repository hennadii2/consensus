import useLabels from "hooks/useLabels";
import React from "react";
import { YesNoType } from "types/YesNoType";

interface MeterTagProps {
  meter?: YesNoType;
}

function MeterTag({ meter }: MeterTagProps) {
  const [meterLabels] = useLabels("meter");

  const label = meterLabels[meter || "YES"];

  if (meter === "NO") {
    return (
      <div className="text-[#E3504F] bg-[#FAE0E0] h-[25px] text-sm flex items-center px-2 md:px-3 rounded-full">
        <span className="bg-[#E3504F] h-[6px] w-[6px] rounded-full" />
        <span data-testid="meter-tag" className="ml-1">
          {label}
        </span>
      </div>
    );
  }
  if (meter === "POSSIBLY") {
    return (
      <div className="text-[#F89C11] bg-[#FEF4d7] h-[25px] text-sm flex items-center px-2 md:px-3 rounded-full">
        <span className="bg-[#F89C11] h-[6px] w-[6px] rounded-full" />
        <span data-testid="meter-tag" className="ml-1">
          {label}
        </span>
      </div>
    );
  }

  if (meter === "YES") {
    return (
      <div className="text-[#46A759] bg-[#DFF1E2] h-[25px] text-sm flex items-center px-2 md:px-3 rounded-full">
        <span className="bg-[#46A759] h-[6px] w-[6px] rounded-full" />
        <span data-testid="meter-tag" className="ml-1">
          {label}
        </span>
      </div>
    );
  }

  if (meter === "UNKNOWN") {
    return (
      <div className="text-[#688092] bg-[#F1F4F6] h-[25px] text-sm flex items-center px-2 md:px-3 rounded-full">
        <span className="bg-[#688092] h-[6px] w-[6px] rounded-full" />
        <span data-testid="meter-tag" className="ml-1">
          {label}
        </span>
      </div>
    );
  }

  return <div data-testid="meter-tag"></div>;
}

export default MeterTag;
