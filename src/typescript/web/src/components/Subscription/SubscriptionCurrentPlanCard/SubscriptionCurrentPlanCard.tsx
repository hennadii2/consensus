import classNames from "classnames";
import { ANNUAL_PRICE_DISCOUNT } from "components/Pricing/PricingSwitch/PricingSwitch";
import { SubscriptionPlan } from "enums/subscription-plans";
import { roundDownSignificantDigits } from "helpers/format";
import {
  getFeatureCopyList,
  getPremiumProduct,
  isSubscriptionCanceledNotExpired,
} from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React, { ReactNode } from "react";
import LoadingSubscriptionCard from "../LoadingSubscriptionCard/LoadingSubscriptionCard";

type Props = {
  children?: ReactNode;
  plan_name: string;
  unit_amount: number;
  interval: string;
  isLifeTimePremium?: boolean;
  subscription?: any;
  isLoading?: boolean;
  onCancelClick?: () => void;
  onResumeClick?: () => void;
  onUpgradeAnnualClick?: () => void;
};

/**
 * @component SubscriptionCurrentPlanCard
 * @description designed for subscription current plan card
 * @example
 * return (
 *   <SubscriptionCurrentPlanCard>Learn more</SubscriptionCurrentPlanCard>
 * )
 */
const SubscriptionCurrentPlanCard = ({
  children,
  plan_name,
  unit_amount,
  interval,
  isLifeTimePremium,
  subscription,
  isLoading,
  onCancelClick,
  onResumeClick,
  onUpgradeAnnualClick,
}: Props) => {
  const [currentPlanCardLabels] = useLabels("current-plan-card");
  const [subscriptionFeaturesLabels] = useLabels("subscription-features");
  const products = useAppSelector((state) => state.subscription.products);
  const currencyFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "usd",
    minimumFractionDigits: 3,
    maximumFractionDigits: 10,
    minimumSignificantDigits: 3,
    maximumSignificantDigits: 10,
  });
  const dateOptions: Intl.DateTimeFormatOptions = {
    month: "long",
    day: "2-digit",
    year: "numeric",
  };

  let features_list = [];
  if (plan_name == SubscriptionPlan.FREE) {
    features_list = subscriptionFeaturesLabels["free-features"];
  } else if (plan_name == SubscriptionPlan.PREMIUM) {
    const premiumProduct = getPremiumProduct(products);
    features_list = getFeatureCopyList(premiumProduct);
  } else if (plan_name == SubscriptionPlan.ENTERPRISE) {
    features_list = subscriptionFeaturesLabels["enterprise-features"];
  }

  let expireDate = null;
  if (
    subscription?.user &&
    isSubscriptionCanceledNotExpired(subscription?.user)
  ) {
    expireDate = new Date(subscription?.user.cancel_at * 1000);
  }

  if (
    subscription?.user &&
    subscription?.user.discount &&
    subscription?.user.discount.coupon
  ) {
    if (
      subscription?.user.discount.coupon.valid &&
      subscription?.user.discount.coupon.percent_off
    ) {
      unit_amount =
        (unit_amount * (100 - subscription?.user.discount.coupon.percent_off)) /
        100;
    }
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
      <div className="flex justify-between">
        <h4 className="text-[#222F2B] font-bold text-lg flex flex-wrap flex-1 items-center">
          <span className="mr-3">{currentPlanCardLabels["title"]}</span>

          {expireDate && (
            <p
              dangerouslySetInnerHTML={{
                __html: currentPlanCardLabels["canceled-expires"].replace(
                  "{value}",
                  expireDate.toLocaleString("en-US", dateOptions)
                ),
              }}
              className="text-xs font-normal bg-[#D9D9D9] rounded-[20px] py-1 px-2 hidden sm:inline-block"
            />
          )}
        </h4>

        {isLifeTimePremium ? (
          <span className="text-sm lg:text-base text-[#222F2B] text-opacity-40 font-bold">
            {currentPlanCardLabels["lifetime-access"]}
          </span>
        ) : onCancelClick && expireDate == null ? (
          <button
            onClick={expireDate ? undefined : onCancelClick}
            data-testid="current-plan-card-cancel-button"
            className={classNames(
              "text-sm lg:text-base text-[#0A6DC2] font-bold",
              expireDate ? "text-[#222F2B66] cursor-not-allowed" : ""
            )}
          >
            {currentPlanCardLabels["cancel-subscription"]}
          </button>
        ) : (
          ""
        )}

        {onResumeClick && expireDate && (
          <button
            className="text-sm lg:text-base text-[#0A6DC2] font-bold"
            onClick={onResumeClick}
          >
            {currentPlanCardLabels["resume-subscription"]}
          </button>
        )}
      </div>

      {expireDate && (
        <p
          dangerouslySetInnerHTML={{
            __html: currentPlanCardLabels["canceled-expires"].replace(
              "{value}",
              expireDate.toLocaleString("en-US", dateOptions)
            ),
          }}
          className="text-xs font-normal bg-[#D9D9D9] rounded-[20px] py-1 px-2 inline-block sm:hidden"
        />
      )}

      <div className="bg-[#F1F4F6] rounded-xl p-5 mt-4 lg:mt-4">
        <div className="flex justify-center flex-wrap">
          <div className="w-full sm:w-[50%] md:w-[50%]">
            <h5
              data-testid="title"
              className="font-bold text-[#222F2B] text-base flex items-center"
            >
              {plan_name == SubscriptionPlan.PREMIUM && (
                <img
                  src={"/icons/premium.svg"}
                  className="w-[24px] h-[24px] mr-1.5"
                  alt="Premium"
                />
              )}
              {plan_name} {currentPlanCardLabels["plan"]}
            </h5>

            {(subscription?.user != null ||
              plan_name == SubscriptionPlan.FREE) && (
              <div className="mt-2.5">
                <span
                  data-testid="current-plan-card-amount"
                  className="text-[#222F2B] text-4xl font-bold"
                >
                  {currencyFormatter.format(
                    Number(
                      roundDownSignificantDigits(unit_amount / 100, 4).toFixed(
                        2
                      )
                    )
                  )}
                </span>
                <span
                  data-testid="current-plan-card-interval"
                  className="text-[#364B44] text-base ml-1"
                >
                  {"/per "}
                  {interval}
                </span>
              </div>
            )}

            {subscription?.user == null && subscription?.org && (
              <div className="mt-2.5">
                <span className="text-[#222F2B] text-4xl font-bold">
                  {subscription?.org.orgName}
                </span>
              </div>
            )}
          </div>

          <div className="w-full sm:w-[50%] md:w-[50%] mt-3 md:mt-0">
            <div
              data-testid="feature-list"
              className="feature-list flex flex-wrap gap-y-2"
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
                  <span className="text-sm sm:text-base leading-tight sm:leading-tight flex-1">
                    {feature}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-5 text-[#0A6DC2] text-base font-bold">
          {subscription?.user != null && interval == "month" ? (
            <button
              className={classNames(
                "relative rounded-full px-5 py-1.5 inline-flex items-center w-full sm:w-auto justify-center",
                "bg-blue-300 text-blue-450",
                "text-sm"
              )}
              type="button"
              onClick={handleClickAnnualUpgrade}
            >
              Save {ANNUAL_PRICE_DISCOUNT} with Annual
            </button>
          ) : (
            <></>
          )}
        </div>
      </div>
    </>
  );
};

export default SubscriptionCurrentPlanCard;
