import { getReversedSubscriptionUsageData } from "helpers/subscription";
import { useAppSelector } from "hooks/useStore";
import React from "react";

type CreditTagProps = {};

/**
 * @component CreditTag
 * @description Component Credit Tag.
 * @example
 * return (
 *   <CreditTag />
 * )
 */
const CreditTag = ({}: CreditTagProps) => {
  const subscriptionUsageData = useAppSelector(
    (state) => state.subscription.usageData
  );
  const reversedSubscriptionUsageData = getReversedSubscriptionUsageData(
    subscriptionUsageData
  );
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  return (
    <span
      data-testid="credit-tag"
      className="rounded-full flex justify-center items-center gap-[4px] h-[30px] bg-white px-[8px]"
    >
      <img
        className="w-[16px] h-[16px] mr-[4px]"
        alt="coin"
        src="/icons/coin-blue.svg"
      />
      <span className="font-bold text-[#009FF5] text-base">
        {reversedSubscriptionUsageData.creditLeft}
      </span>
    </span>
  );
};

export default CreditTag;
