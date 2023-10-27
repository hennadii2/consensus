import Button from "components/Button";
import {
  getReversedSubscriptionUsageData,
  isSubscriptionPremium,
} from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import React, { useCallback } from "react";
import { setOpenUpgradeToPremiumPopup } from "store/slices/subscription";

/**
 * @component StudyDetailsTooltip
 * @description Tooltip for case study
 * @example
 * return (
 *   <StudyDetailsTooltip />
 * )
 */
const StudyDetailsTooltip = () => {
  const [tooltipsLabels] = useLabels("tooltips.study-details");
  const dispatch = useAppDispatch();
  const subscription = useAppSelector(
    (state) => state.subscription.subscription
  );
  const subscriptionUsageData = useAppSelector(
    (state) => state.subscription.usageData
  );
  const reversedSubscriptionUsageData = getReversedSubscriptionUsageData(
    subscriptionUsageData
  );
  const isPremium = isSubscriptionPremium(subscription);
  const handleClickUpgradePremium = useCallback(async () => {
    dispatch(setOpenUpgradeToPremiumPopup(true));
  }, [dispatch]);

  return (
    <div className="text-[#364B44]" data-testid="tooltip-study-details">
      <div className="flex flex-row items-center gap-x-[6px] mb-3">
        <img
          className="min-w-[24px] max-w-[24px] h-6 w-6 ml-1 mr-[6px]"
          alt="Sparkler"
          src="/icons/sparkler.svg"
        />
        <p className="font-bold text-lg flex items-center">
          {tooltipsLabels["title"]}
        </p>
      </div>
      <p
        className="text-base mb-[16px]"
        dangerouslySetInnerHTML={{ __html: tooltipsLabels["content"] }}
      ></p>

      {isPremium && (
        <>
          <p className="font-bold text-lg text-[#364B44] flex items-center">
            <img
              src={"/icons/premium.svg"}
              className="w-[24px] h-[24px] mr-2"
              alt="Premium"
            />
            {tooltipsLabels["premium-plan"]}
          </p>
          <p
            className="mt-2 text-base text-[#688092]"
            dangerouslySetInnerHTML={{
              __html: tooltipsLabels["premium-plan-description"],
            }}
          ></p>
        </>
      )}

      {!isPremium && (
        <>
          <div className="flex items-center">
            <img
              className="w-[16px] h-[16px] mr-[6px]"
              alt="coin"
              src="/icons/coin-blue.svg"
            />

            <span className="text-base text-[#364B44] font-bold mr-1">{`${tooltipsLabels["ai-credits-left"]} - `}</span>
            <span className="text-base text-[#57AC91] font-bold">
              {reversedSubscriptionUsageData.creditLeft}
            </span>
          </div>

          <div className="mt-[4px] text-sm text-[#688092]">
            <span className="mr-1">{tooltipsLabels["renews-on"]}</span>
            <span className="font-bold">
              {reversedSubscriptionUsageData.refreshDate}
            </span>
          </div>

          <Button
            type="button"
            className="bg-[#0A6DC2] text-white text-center justify-center flex items-center text-sm rounded-full mt-[16px] py-[7px] pl-5 pr-5"
            onClick={handleClickUpgradePremium}
          >
            {tooltipsLabels["upgrade-to-premium"]}
          </Button>
        </>
      )}
    </div>
  );
};

export default StudyDetailsTooltip;
