import classNames from "classnames";
import React, { useEffect, useState } from "react";

export enum PricingSwitchFlag {
  MONTHLY = "monthly",
  ANNUALLY = "annually",
}

export const ANNUAL_PRICE_DISCOUNT = "30%";

type PricingSwitchProps = {
  onChange: (flag: PricingSwitchFlag) => void;
  initialFlag: PricingSwitchFlag;
  className?: string;
};

function PricingSwitch({
  onChange,
  initialFlag = PricingSwitchFlag.MONTHLY,
  className,
}: PricingSwitchProps) {
  const [activeFlag, setActiveFlag] = useState(initialFlag);

  if (!onChange) {
    throw new Error("onChange props is required!");
  }

  const handleClickMonthlyToggle = () => {
    setActiveFlag(PricingSwitchFlag.MONTHLY);
    onChange(PricingSwitchFlag.MONTHLY);
  };

  const handleClickAnnuallyToggle = () => {
    setActiveFlag(PricingSwitchFlag.ANNUALLY);
    onChange(PricingSwitchFlag.ANNUALLY);
  };

  useEffect(() => {
    // Update state if change made after initializatin of componenet
    setActiveFlag(initialFlag);
  }, [initialFlag]);

  return (
    <div
      data-testid="pricing-switch"
      className={classNames(
        "bg-white rounded-full inline-flex ml-[auto] mr-[auto] p-1 md:p-2",
        className || ""
      )}
    >
      <button
        className={classNames(
          "relative rounded-full px-3 py-1 md:px-5 md:py-1.5",
          activeFlag == PricingSwitchFlag.MONTHLY
            ? "bg-gray-100 text-green-650 font-bold"
            : "text-black",
          "text-base"
        )}
        type="button"
        data-testid="pricing-switch-monthly"
        onClick={handleClickMonthlyToggle}
      >
        Monthly
      </button>

      <button
        className={classNames(
          "relative rounded-full px-3 py-1 md:px-5 md:py-1.5 inline-flex items-center",
          activeFlag == PricingSwitchFlag.ANNUALLY
            ? "bg-gray-100 text-green-650 font-bold"
            : "text-black",
          "text-base"
        )}
        type="button"
        data-testid="pricing-switch-annually"
        onClick={handleClickAnnuallyToggle}
      >
        Annually
        <div className="bg-green-200-op-16 text-sm text-green-500 ml-1.5 pl-1.5 pr-1.5 pt-1 pb-1 rounded-full">
          Save {ANNUAL_PRICE_DISCOUNT}
        </div>
      </button>
    </div>
  );
}

export default PricingSwitch;
