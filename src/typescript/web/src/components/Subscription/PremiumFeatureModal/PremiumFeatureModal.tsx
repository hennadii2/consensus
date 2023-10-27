import { useQuery } from "@tanstack/react-query";
import Modal from "components/Modal";
import PricingSwitch, {
  PricingSwitchFlag,
} from "components/Pricing/PricingSwitch/PricingSwitch";
import { roundDownSignificantDigits } from "helpers/format";
import { pricingPageUrl } from "helpers/pageUrl";
import { getMonthAnnualPrices } from "helpers/products";
import {
  getFeatureCopyList,
  getPremiumProduct,
  getSubscriptionProducts,
} from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import { useRouter } from "next/router";
import React, { useCallback, useState } from "react";
import {
  setOpenUpgradeToPremiumPopup,
  setProducts,
} from "store/slices/subscription";
import { useSubscription } from "../SubscriptionProvider/SubscriptionProvider";

/**
 * @component PremiumFeatureModal
 * @description Component for premium feature modal
 * @example
 * return (
 *   <PremiumFeatureModal />
 * )
 */
function PremiumFeatureModal() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const isOpen = useAppSelector(
    (state) => state.subscription.openUpgradeToPremiumPopup
  );
  const [pageLabels] = useLabels("premium-feature-modal");
  const [subscriptionFeaturesLabels] = useLabels("subscription-features");
  const [activeFlag, setActiveFlag] = useState(PricingSwitchFlag.ANNUALLY);
  const products = useAppSelector((state) => state.subscription.products);
  let features_list: string[] = [];
  const currencyFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "usd",
    minimumFractionDigits: 3,
    maximumFractionDigits: 10,
    minimumSignificantDigits: 3,
    maximumSignificantDigits: 10,
  });
  const { redirectToCheckout } = useSubscription();

  useQuery(
    ["subscription-products-query"],
    async () => {
      const sortedProducts = await getSubscriptionProducts();
      dispatch(setProducts(sortedProducts));
    },
    {
      enabled: isOpen,
    }
  );
  const premiumProduct = getPremiumProduct(products);
  if (premiumProduct) {
    features_list = getFeatureCopyList(premiumProduct);
  }
  let { monthPrice, annualPrice } = getMonthAnnualPrices(products);

  const closePopup = useCallback(async () => {
    dispatch(setOpenUpgradeToPremiumPopup(false));
  }, [dispatch]);

  const handleClickUpgrade = () => {
    closePopup();
    if (activeFlag == PricingSwitchFlag.MONTHLY && monthPrice) {
      redirectToCheckout({ price: monthPrice.id });
    }

    if (activeFlag == PricingSwitchFlag.ANNUALLY && annualPrice) {
      redirectToCheckout({ price: annualPrice.id });
    }
  };

  const handleClickPricing = () => {
    closePopup();
    router.push(pricingPageUrl());
  };

  return (
    <>
      <Modal
        open={isOpen}
        onClose={closePopup}
        size="md"
        padding={false}
        overflowVisible={true}
        mobileFit={true}
        additionalClass={"mt-[60px]"}
      >
        <div
          className="p-12 bg-[url('/images/bg-card.webp')] bg-no-repeat text-[#364B44] leading-tight rounded-lg"
          data-testid="premium-feature-modal"
        >
          <div className="text-center translate-y-[-50%] translate-x-[-50%] absolute left-[50%] top-0">
            <span className="inline-block bg-white p-5 rounded-full">
              <img
                src={"/icons/premium.svg"}
                className="w-[64px] h-[64px]"
                alt="Premium"
              />
            </span>
          </div>
          <div>
            <h3 className="text-2xl text-center font-bold ax-w-sm mx-auto mt-8">
              {pageLabels["title"]}
            </h3>
          </div>

          <div className="mt-2">
            {activeFlag == PricingSwitchFlag.MONTHLY && monthPrice && (
              <div className="text-center">
                <span className="font-bold text-4xl">
                  {currencyFormatter.format(
                    roundDownSignificantDigits(monthPrice.unit_amount / 100, 3)
                  )}
                </span>
                <span className="text-lg text-[#688092]">
                  {" "}
                  /{pageLabels["per-month"]}
                </span>
              </div>
            )}

            {activeFlag == PricingSwitchFlag.ANNUALLY && annualPrice && (
              <div className="text-center">
                <span className="font-bold text-4xl">
                  {currencyFormatter.format(
                    roundDownSignificantDigits(
                      annualPrice.unit_amount / 12 / 100,
                      3
                    )
                  )}
                </span>
                <span className="text-lg text-[#688092]">
                  {" "}
                  /{pageLabels["per-month"]}
                </span>
              </div>
            )}
          </div>

          <div className="text-center mt-5">
            <PricingSwitch
              onChange={(currentFlag) => {
                setActiveFlag(currentFlag);
              }}
              initialFlag={PricingSwitchFlag.ANNUALLY}
            />
          </div>

          <div className="text-center mt-6">
            <div className="inline-block flex-wrap">
              {features_list.map((feature: any) => (
                <div
                  key={`feature-${feature}`}
                  className="feture-list-item flex items-center align-center gap-x-2 mt-2"
                >
                  <img
                    src={"/icons/check-mark.svg"}
                    className="w-[20px] h-[20px] text-sm"
                    alt="check-mark"
                  />
                  <span className="text-sm sm:text-base text-left leading-tight flex-1">
                    {feature}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-8">
            <button
              onClick={handleClickUpgrade}
              className="flex w-full justify-center bg-[#0A6DC2] text-white py-3 rounded-full items-center cursor-pointer"
            >
              {pageLabels["button-upgrade"]}
            </button>
          </div>

          <div className="mt-4">
            <button
              onClick={handleClickPricing}
              className="flex w-full justify-center bg-[#D3EAFD] text-[#085394] py-3 rounded-full items-center cursor-pointer"
            >
              {pageLabels["button-pricing"]}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}

export default PremiumFeatureModal;
