import { useAuth } from "@clerk/nextjs";
import { SubscriptionPlan } from "enums/subscription-plans";
import { roundDownSignificantDigits } from "helpers/format";
import { pricingPageUrl } from "helpers/pageUrl";
import useLabels from "hooks/useLabels";
import Link from "next/link";
import React, { ReactNode } from "react";
import LoadingSubscriptionCard from "../LoadingSubscriptionCard/LoadingSubscriptionCard";

type Props = {
  children?: ReactNode;
  upgradePlan: SubscriptionPlan;
  unit_amount?: number;
  interval?: string;
  isLoading?: boolean;
  onClick?: () => void;
};

/**
 * @component SubscriptionUpgradeCard
 * @description designed for subscription upgrade card
 * @example
 * return (
 *   <SubscriptionUpgradeCard>Learn more</SubscriptionUpgradeCard>
 * )
 */
const SubscriptionUpgradeCard = ({
  children,
  upgradePlan,
  unit_amount,
  interval,
  isLoading,
  onClick,
}: Props) => {
  const { isSignedIn, isLoaded } = useAuth();
  const [upgradePlanLabels] = useLabels("upgrade-plan-card");
  const currencyFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "usd",
    minimumFractionDigits: 3,
    maximumFractionDigits: 10,
    minimumSignificantDigits: 3,
    maximumSignificantDigits: 10,
  });

  let title =
    upgradePlan == SubscriptionPlan.PREMIUM
      ? upgradePlanLabels["title-premium"]
      : upgradePlanLabels["title-enterprise"];

  if (isLoading) {
    return <LoadingSubscriptionCard />;
  }
  return (
    <>
      <div className="flex flex-wrap">
        <div className="flex-1">
          <div className="flex flex-wrap justify-between items-center">
            {upgradePlan == SubscriptionPlan.PREMIUM ? (
              <img
                alt="Premium"
                className="w-[60px] h-[60px]"
                src="/icons/premium.svg"
              />
            ) : (
              <img
                alt="Enterprise"
                className="w-[60px] h-[60px]"
                src="/icons/enterprise.svg"
              />
            )}

            <Link href={pricingPageUrl()} legacyBehavior>
              <a className="mr-5 mt-[-12px] text-base font-bold text-blue-450 hidden lg:inline-block">
                {upgradePlanLabels["view-our-pricing"]}
              </a>
            </Link>

            <h4
              data-testid="title"
              className="text-[#57AC91] font-bold text-[22px] leading-tight flex-1 ml-3 lg:ml-0 lg:w-full lg:flex-none lg:mt-5"
            >
              {title}
            </h4>
          </div>

          {upgradePlan == SubscriptionPlan.PREMIUM &&
            unit_amount != undefined &&
            interval != undefined && (
              <div className="mt-2">
                <span
                  data-testid="upgrade-plan-card-amount"
                  className="text-[#222F2B] text-4xl font-bold"
                >
                  {currencyFormatter.format(
                    roundDownSignificantDigits(unit_amount / 100, 3)
                  )}
                </span>
                <span
                  data-testid="current-plan-card-interval"
                  className="text-[#364B44] text-base ml-1"
                >
                  {"/ "}
                  {upgradePlanLabels["per-month"]}
                </span>

                {interval == "year" && (
                  <span className="text-[#364B44] text-base ml-1">
                    {upgradePlanLabels["billed-annually"]}
                  </span>
                )}
              </div>
            )}

          {upgradePlan == SubscriptionPlan.ENTERPRISE && (
            <p className="mt-2.5 text-base leading-tight text-[#364B44]">
              {upgradePlanLabels["description-enterprise"]}
            </p>
          )}
        </div>

        <div className="w-full mt-6 lg:w-[auto] lg:mt-0 text-center sm:text-left">
          <Link href={pricingPageUrl()} legacyBehavior>
            <a className="text-base font-bold text-blue-450 inline-block lg:hidden">
              {upgradePlanLabels["view-our-pricing"]}
            </a>
          </Link>

          <button
            data-testid="upgrade-card-button"
            type="button"
            className="transition bg-[#0A6DC2] h-[44px] mt-4 w-full sm:w-auto lg:mt-0 flex items-center justify-center text-white text-base leading-tight rounded-full pt-1.5 pb-1.5 pl-5 pr-5"
            onClick={onClick}
          >
            {isLoaded && !isSignedIn
              ? upgradePlanLabels["get-access"]
              : upgradePlan == SubscriptionPlan.PREMIUM
              ? upgradePlanLabels["upgrade-plan"]
              : upgradePlanLabels["contact-sales"]}
          </button>
        </div>
      </div>
    </>
  );
};

export default SubscriptionUpgradeCard;
