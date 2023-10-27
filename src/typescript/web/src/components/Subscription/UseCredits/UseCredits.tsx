import { MAX_CREDIT_NUM } from "constants/config";
import { pricingPageUrl } from "helpers/pageUrl";
import { getReversedSubscriptionUsageData } from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import Link from "next/link";
import { useRouter } from "next/router";
import React from "react";
import {
  setOpenUpgradeToPremiumPopup,
  setUseCredit,
} from "store/slices/subscription";

/**
 * @component UseCreditsModal
 * @description Component for Use Credits
 * @example
 * return (
 *   <UseCreditsModal
 *    open={true}
 *    onClose={fn}
 *   />
 * )
 */
function UseCredits() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const [pageLabels] = useLabels("use-credit-modal");
  const subscriptionUsageData = useAppSelector(
    (state) => state.subscription.usageData
  );
  const reversedSubscriptionUsageData = getReversedSubscriptionUsageData(
    subscriptionUsageData
  );

  const onClickUpgradeToPremium = () => {
    dispatch(setOpenUpgradeToPremiumPopup(true));
  };

  const handleClickUseCredits = () => {
    dispatch(setUseCredit(true));
  };

  if (!subscriptionUsageData.isSet) {
    return <></>;
  }

  return (
    <>
      <div
        style={{
          background: "#FFFFFF",
          boxShadow: "-4px -2px 25px rgba(104, 104, 104, 0.2)",
        }}
        className="p-5 text-[#364B44] leading-tight rounded-lg w-full"
        data-testid="use-credit-widget"
      >
        <div>
          {reversedSubscriptionUsageData.creditLeft == 0 && (
            <>
              <div className="flex flex-wrap items-center justify-between">
                <h3 className="text-lg font-bold mr-2">
                  {pageLabels["no-credits-title"]}
                </h3>

                <div className="text-sm text-blue-350 w-full mt-1.5 sm:w-auto sm:mt-1.5">
                  <span className="mr-1">{pageLabels["renews-on"]}</span>
                  <strong>{reversedSubscriptionUsageData.refreshDate}</strong>
                </div>
              </div>

              <div className="flex mt-4 gap-x-3">
                <div className="inline-block p-2.5 rounded-lg bg-gray-100 h-fit">
                  <img
                    src={"/icons/premium.svg"}
                    className="w-[24px] h-[24px]"
                    alt="premium icon"
                  />
                </div>

                <div className="flex-1">
                  <p
                    className="text-sm text-green-650"
                    dangerouslySetInnerHTML={{
                      __html: pageLabels["unlock-with-premium"].replace(
                        "{max-count}",
                        MAX_CREDIT_NUM
                      ),
                    }}
                  ></p>
                  <div className="mt-1 text-sm text-blue-350">
                    <span className="">{pageLabels["pricing-text1"]}</span>
                    <Link href={pricingPageUrl()} legacyBehavior>
                      <a className="text-[#2AA3EF] font-bold ml-1">
                        {pageLabels["pricing"]}
                      </a>
                    </Link>
                    <span className="ml-1">{pageLabels["pricing-text2"]}</span>
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap items-center sm:flex-nowrap justify-between text-sm mt-4">
                <div className="text-black">
                  <span>{pageLabels["want-unlimited"]}</span>
                </div>

                <div className="inline-flex justify-left w-full sm:w-auto mt-3 sm:mt-0">
                  <button
                    onClick={onClickUpgradeToPremium}
                    className="bg-[#0A6DC2] text-white text-sm px-5 py-1.5 rounded-full"
                  >
                    {pageLabels["upgrade-to-premium"]}
                  </button>
                </div>
              </div>
            </>
          )}

          {reversedSubscriptionUsageData.creditLeft > 0 && (
            <>
              <div className="w-full flex items-center mt-4">
                <div className="inline-block w-[6px] h-[6px] rounded-full bg-[#364B44]"></div>

                <div className="flex-1 ml-3.5 text-[#364B44] text-sm lg:text-base items-center flex">
                  <span data-testid="no-credits-left-title" className="">
                    {pageLabels["credits-left"]}
                  </span>
                  <span className="ml-1 mr-1 inline-block">{"-"}</span>
                  <span data-testid="no-credit-left-num" className="font-bold">
                    {reversedSubscriptionUsageData.creditLeft}
                  </span>
                </div>
              </div>

              <div className="flex flex-wrap items-center justify-between text-sm mt-5">
                <div className="inline-flex flex-wrap flex-1">
                  <span className="w-full sm:w-auto">
                    {pageLabels["want-unlimited"]}
                  </span>
                  <button
                    onClick={onClickUpgradeToPremium}
                    className="text-[#0A6DC2] text-left font-bold ml-0 mt-1 sm:ml-1 sm:mt-0"
                  >
                    {pageLabels["upgrade-to-premium"]}
                  </button>
                </div>

                <div className="inline-flex">
                  <button
                    onClick={handleClickUseCredits}
                    className="bg-[#D3EAFD] text-[#0A6DC2] pt-2 pb-2 pl-5 pr-5 rounded-full"
                  >
                    {pageLabels["use-credits-button"]}
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}

export default UseCredits;
