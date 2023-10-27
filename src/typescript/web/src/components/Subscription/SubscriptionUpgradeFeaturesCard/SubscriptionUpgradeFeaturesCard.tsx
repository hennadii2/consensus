import classNames from "classnames";
import { ANNUAL_PRICE_DISCOUNT } from "components/Pricing/PricingSwitch/PricingSwitch";
import { SubscriptionPlan } from "enums/subscription-plans";
import { getFeatureCopyList, getPremiumProduct } from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React, { ReactNode } from "react";
import LoadingSubscriptionCard from "../LoadingSubscriptionCard/LoadingSubscriptionCard";

type Props = {
  children?: ReactNode;
  plan_name?: SubscriptionPlan;
  onUpgradeAnnualClick?: () => void;
  isLoading?: boolean;
};

/**
 * @component SubscriptionUpgradeFeaturesCard
 * @description designed for subscription current plan card
 * @example
 * return (
 *   <SubscriptionUpgradeFeaturesCard>Learn more</SubscriptionUpgradeFeaturesCard>
 * )
 */
const SubscriptionUpgradeFeaturesCard = ({
  children,
  plan_name,
  onUpgradeAnnualClick,
  isLoading,
}: Props) => {
  const [upgradeFeaturesCardLabels] = useLabels("upgrade-features-card");
  const [subscriptionFeaturesLabels] = useLabels("subscription-features");
  const products = useAppSelector((state) => state.subscription.products);

  let features_list = [];
  if (plan_name == SubscriptionPlan.FREE) {
    features_list = subscriptionFeaturesLabels["free-features"];
  } else if (plan_name == SubscriptionPlan.PREMIUM) {
    const premiumProduct = getPremiumProduct(products);
    features_list = getFeatureCopyList(premiumProduct);
  } else if (plan_name == SubscriptionPlan.ENTERPRISE) {
    features_list = subscriptionFeaturesLabels["enterprise-features"];
  }

  const handleClickAnnualUpgrade = () => {
    if (onUpgradeAnnualClick) {
      onUpgradeAnnualClick();
    }
  };

  if (isLoading) {
    return <LoadingSubscriptionCard />;
  }

  return (
    <>
      <div className="flex flex-wrap justify-between">
        <div className="flex-1">
          <h4 data-testid="title" className="text-white font-bold text-lg pr-4">
            {upgradeFeaturesCardLabels["title"]}
          </h4>

          <div
            data-testid="feature-list"
            className="feature-list flex flex-wrap gap-y-2 mt-4"
          >
            {features_list.map((feature: any) => (
              <div
                key={`feature-${feature}`}
                className="feture-list-item w-full flex items-start gap-x-2"
              >
                <img
                  src={"/icons/check-mark.svg"}
                  className="w-[16px] h-[16px] mt-0.5"
                  alt="check-mark icon"
                />
                <span className="text-sm sm:text-base leading-tight sm:leading-tight flex-1 text-white">
                  {feature}
                </span>
              </div>
            ))}
          </div>

          <button
            className={classNames(
              "relative rounded-full px-5 py-1.5 inline-flex items-center w-full sm:w-auto justify-center",
              "bg-gray-100 text-blue-450 text-sm mt-6 lg:mt-4"
            )}
            type="button"
            onClick={handleClickAnnualUpgrade}
          >
            Save {ANNUAL_PRICE_DISCOUNT} with Annual
          </button>
        </div>
      </div>
    </>
  );
};

export default SubscriptionUpgradeFeaturesCard;
