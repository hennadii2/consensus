import classNames from "classnames";
import React, { useEffect, useState } from "react";

type SwitchProps = {
  onChange: (state: boolean) => void;
  active?: boolean;
  disabled?: boolean;
  className?: string;
};

function Switch({
  onChange,
  active = false,
  disabled = false,
  className,
}: SwitchProps) {
  const [isActive, setIsActive] = useState(active);

  if (!onChange) {
    throw new Error("onChange props is required!");
  }

  const toggleIsActive = () => {
    if (!disabled) {
      setIsActive(!isActive);
      onChange(!isActive);
    }
  };

  useEffect(() => {
    // Update state if change made after initializatin of componenet
    setIsActive(active);
  }, [active]);

  return (
    <button
      className={classNames(
        "transition relative w-[29px] h-[16px] rounded-full",
        disabled ? "bg-[#DEE0E3]" : isActive ? "bg-[#57AC91]" : "bg-[#70707C]",
        className || ""
      )}
      type="button"
      data-state={isActive ? "on" : "off"}
      data-testid="switch"
      onClick={toggleIsActive}
    >
      <div
        className={classNames(
          "transition absolute w-[12px] h-[12px] top-1/2 -translate-y-1/2 rounded-full bg-[#F5F5FF] grid place-items-center",
          !isActive ? "left-[2px]" : "left-[15px]"
        )}
      >
        {isActive && (
          <div className="h-[4px] w-[4px] bg-[#57AC91] rounded-full"></div>
        )}
      </div>
    </button>
  );
}

export default Switch;
