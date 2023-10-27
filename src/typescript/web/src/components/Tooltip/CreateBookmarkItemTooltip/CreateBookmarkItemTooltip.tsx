import Button from "components/Button";
import { pricingPageUrl } from "helpers/pageUrl";
import { isSubscriptionPremium } from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import Link from "next/link";
import React, { useCallback } from "react";
import { setOpenUpgradeToPremiumPopup } from "store/slices/subscription";

/**
 * @component CreateBookmarkItemTooltip
 * @description Tooltip for Create bookmark item
 * @example
 * return (
 *   <CreateBookmarkItemTooltip />
 * )
 */

interface CreateBookmarkItemTooltipProps {
  onClick?: () => void;
}

function CreateBookmarkItemTooltip({
  onClick,
}: CreateBookmarkItemTooltipProps) {
  const dispatch = useAppDispatch();
  const [bookmarkPremiumTooltipLabels] = useLabels(
    "tooltips.bookmark-premium-tooltip"
  );
  const subscription = useAppSelector(
    (state) => state.subscription.subscription
  );
  const subscriptionUsageData = useAppSelector(
    (state) => state.subscription.usageData
  );

  const handleClickUpgradePremium = useCallback(async () => {
    if (onClick != null) {
      onClick();
    }

    dispatch(setOpenUpgradeToPremiumPopup(true));
  }, [dispatch, onClick]);

  const isPremium = isSubscriptionPremium(subscription);

  return (
    <div
      className="p-2 text-[#364B44] leading-tight"
      data-testid="tooltip-create-bookmark-list"
    >
      <div className="">
        {!isPremium && (
          <>
            <p className="font-bold text-lg">
              {bookmarkPremiumTooltipLabels["free-plan"]}
            </p>
            <p
              className="mt-2 text-base text-black"
              dangerouslySetInnerHTML={{
                __html:
                  bookmarkPremiumTooltipLabels["limited-items-description"],
              }}
            ></p>

            <div className="flex justify-between mt-[20px]">
              <Link href={pricingPageUrl()} legacyBehavior>
                <a className="text-[#0A6DC2] text-sm font-bold">
                  {bookmarkPremiumTooltipLabels["view-pricing"]}
                </a>
              </Link>

              <Button
                type="button"
                className="text-[#0A6DC2] justify-center flex items-center text-sm font-bold gap-x-[8px]"
                onClick={handleClickUpgradePremium}
              >
                <img
                  src={"/icons/premium.svg"}
                  className="w-[20px] h-[20px]"
                  alt="premium icon"
                />
                {bookmarkPremiumTooltipLabels["upgrade-to-premium"]}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default CreateBookmarkItemTooltip;
