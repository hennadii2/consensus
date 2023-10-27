import Button from "components/Button";
import {
  getReversedSubscriptionUsageData,
  isSubscriptionPremium,
} from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React from "react";

/**
 * @component SynthesizeToggleTooltip
 * @description Tooltip for Synthesize Toggle for unlocked state
 * @example
 * return (
 *   <SynthesizeToggleTooltip />
 * )
 */

interface SynthesizeToggleTooltipProps {
  onClickUpgradeToPremium?: () => void;
}

function SynthesizeToggleTooltip({
  onClickUpgradeToPremium,
}: SynthesizeToggleTooltipProps) {
  const [synthesizeToggleUnlockedLabels] = useLabels(
    "tooltips.synthesize-toggle.unlocked"
  );
  const subscription = useAppSelector(
    (state) => state.subscription.subscription
  );
  const subscriptionUsageData = useAppSelector(
    (state) => state.subscription.usageData
  );
  const reversedSubscriptionUsageData = getReversedSubscriptionUsageData(
    subscriptionUsageData
  );

  const handleClickUpgradePremium = async () => {
    if (onClickUpgradeToPremium) {
      onClickUpgradeToPremium();
    }
  };

  const isPremium = isSubscriptionPremium(subscription);

  return (
    <div
      className="p-2 text-[#364B44] leading-tight"
      data-testid="tooltip-score"
    >
      <p className="font-bold mt-1 mb-3 text-lg flex items-center">
        <img
          className="w-[24px] h-[24px] mr-[6px]"
          alt="Sparkler"
          src="/icons/sparkler.svg"
        />

        {isPremium
          ? synthesizeToggleUnlockedLabels["premium-title"]
          : synthesizeToggleUnlockedLabels["free-title"]}
      </p>
      <p className="text-base">
        {synthesizeToggleUnlockedLabels["description"]}
      </p>

      <div className="mt-[16px]">
        {isPremium && (
          <>
            <p className="font-bold text-lg flex items-center">
              <img
                src={"/icons/premium.svg"}
                className="w-[24px] h-[24px] mr-2"
                alt="Premium"
              />
              {synthesizeToggleUnlockedLabels["premium-plan"]}
            </p>
            <p
              className="mt-2 text-base text-[#688092]"
              dangerouslySetInnerHTML={{
                __html:
                  synthesizeToggleUnlockedLabels["premium-plan-description"],
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

              <span className="text-base text-[#364B44] font-bold mr-1">{`${synthesizeToggleUnlockedLabels["ai-credits-left"]} - `}</span>
              <span className="text-base text-[#57AC91] font-bold">
                {reversedSubscriptionUsageData.creditLeft}
              </span>
            </div>

            <div className="mt-[4px] text-sm text-[#688092]">
              <span className="mr-1">
                {synthesizeToggleUnlockedLabels["renews-on"]}
              </span>
              <span className="font-bold">
                {reversedSubscriptionUsageData.refreshDate}
              </span>
            </div>

            <Button
              type="button"
              className="bg-[#0A6DC2] text-white text-center justify-center flex items-center text-sm rounded-full mt-[16px] pt-2.5 pb-2.5 pl-5 pr-5"
              onClick={handleClickUpgradePremium}
            >
              {synthesizeToggleUnlockedLabels["upgrade-to-premium"]}
            </Button>
          </>
        )}
      </div>
    </div>
  );
}

export default SynthesizeToggleTooltip;
