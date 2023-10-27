import { useAuth } from "@clerk/nextjs";
import classNames from "classnames";
import {
  SALES_EMAIL,
  STRIPE_PRICE_METADATA_TYPE_EARLY_BIRD,
  STRIPE_PRICE_METADATA_TYPE_LIFETIME,
} from "constants/config";
import { SubscriptionPlan } from "enums/subscription-plans";
import { roundDownSignificantDigits } from "helpers/format";
import { findSubscriptionProduct } from "helpers/products";
import {
  getFeatureCopyList,
  isSubscriptionCanceledNotExpired,
  ISubscriptionData,
} from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React from "react";
import LoadingPricingCard from "../LoadingPricingCard/LoadingPricingCard";

type PricingCardProps = {
  onClick: (price?: any) => void;
  title?: string;
  product?: any;
  price?: any;
  subscription?: ISubscriptionData;
  className?: string;
  isLoading?: boolean;
  isTest?: boolean;
};

function PricingCard({
  onClick,
  title,
  product,
  price,
  subscription,
  className,
  isLoading,
  isTest,
}: PricingCardProps) {
  const { isSignedIn, isLoaded } = useAuth();
  const [pricingLabels] = useLabels("screens.pricing");
  const [subscriptionFeaturesLabels] = useLabels("subscription-features");
  const currencyFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "usd",
    minimumFractionDigits: 3,
    maximumFractionDigits: 10,
    minimumSignificantDigits: 3,
    maximumSignificantDigits: 10,
  });
  const products = useAppSelector((state) => state.subscription.products);
  const subscriptionProduct = findSubscriptionProduct(products, subscription);
  const isSubscriptionLifeTimePremium = Boolean(
    subscriptionProduct &&
      subscriptionProduct.price &&
      subscriptionProduct.price.metadata.type ==
        STRIPE_PRICE_METADATA_TYPE_LIFETIME
  );
  const isSubscriptionEarlyBirdPremium = Boolean(
    subscriptionProduct &&
      subscriptionProduct.price &&
      subscriptionProduct.price.metadata.type ==
        STRIPE_PRICE_METADATA_TYPE_EARLY_BIRD
  );

  let features_list = [];
  let description;
  let buttonText = "";
  let unitAmountMonth = 0.0;
  let buttonDisable = false;
  let buttonVisible = true;

  if (title == SubscriptionPlan.FREE) {
    features_list = subscriptionFeaturesLabels["free-features"];
  } else if (title == SubscriptionPlan.ENTERPRISE) {
    features_list = subscriptionFeaturesLabels["enterprise-features"];
    description = pricingLabels["enterprise-description"];
  } else {
    title = SubscriptionPlan.PREMIUM;
    features_list = getFeatureCopyList(product);
    description = pricingLabels["premium-description"];
  }

  if (title == SubscriptionPlan.PREMIUM && isSubscriptionLifeTimePremium) {
    buttonText = pricingLabels["current-plan"];
    buttonDisable = true;
  }
  if (title == SubscriptionPlan.PREMIUM && isSubscriptionEarlyBirdPremium) {
    buttonText = pricingLabels["upgrade-plan"];
    buttonDisable = false;
  } else if (title == SubscriptionPlan.FREE) {
    buttonText = pricingLabels["current-plan"];
    buttonDisable = true;

    if (isLoaded && isSignedIn) {
      if (subscription?.user) {
        buttonVisible = false;
      }
    } else {
      buttonText = pricingLabels["try-searching-for-free"];
      buttonDisable = false;
    }
  } else if (title == SubscriptionPlan.ENTERPRISE) {
    buttonText = pricingLabels["contact-sales"];
  } else if (title == SubscriptionPlan.PREMIUM && price) {
    if (subscription?.user) {
      if (price.id == subscription?.user.plan.id) {
        buttonText = pricingLabels["current-plan"];
        buttonDisable = true;
      } else {
        buttonText = pricingLabels["current-plan"];
        buttonDisable = true;
      }

      if (isSubscriptionCanceledNotExpired(subscription?.user)) {
        buttonText = pricingLabels["upgrade-plan"];
        buttonDisable = false;
      }
    } else {
      if (isLoaded && isSignedIn) {
        buttonText = pricingLabels["upgrade-plan"];
      } else {
        buttonText = pricingLabels["get-access"];
      }
    }
  }

  if (price && price?.recurring) {
    if (price?.recurring.interval == "year") {
      unitAmountMonth = price?.unit_amount / 12.0;
    } else {
      unitAmountMonth = price?.unit_amount / 1.0;
    }
  }

  const handleClickButton = () => {
    if (title == SubscriptionPlan.ENTERPRISE) {
      window.location.href = "mailto:" + SALES_EMAIL;
    }

    if (onClick) {
      onClick(price ? price : null);
    }
  };

  if (isLoading && !isTest) {
    return (
      <>
        <LoadingPricingCard />
      </>
    );
  }

  return (
    <div
      data-testid="pricing-card"
      className={classNames(
        "pricing-card rounded-2xl p-6 h-full flex flex-wrap flex-col content-start",
        title == "Premium" ? "pricing-card-highlight text-white" : "",
        className || ""
      )}
    >
      <h3
        data-testid="pricing-card-title"
        className="text-lg font-bold mb-1 md:mb-4 w-full"
      >
        {title}
      </h3>

      {price ? (
        <div className="mb-3 md:mb-8 w-full">
          <span
            className="text-3xl font-bold"
            data-testid="pricing-card-unit-amount"
          >
            {currencyFormatter.format(
              roundDownSignificantDigits(unitAmountMonth / 100, 3)
            )}
          </span>
          <span className="text-lg"> /{pricingLabels["per-month"]}</span>

          {price?.recurring.interval == "year" && (
            <span className="text-lg ml-1">
              {pricingLabels["billed-annually"]}
            </span>
          )}
        </div>
      ) : title == SubscriptionPlan.FREE ? (
        <div className="mb-3 md:mb-8 w-full">
          <span
            className="text-3xl font-bold"
            data-testid="pricing-card-unit-amount"
          >
            {currencyFormatter.format(roundDownSignificantDigits(0, 3))}
          </span>
          <span className="text-lg"> /{pricingLabels["per-month"]}</span>
        </div>
      ) : title == SubscriptionPlan.ENTERPRISE ? (
        <div className="mb-3 md:mb-8 w-full">
          <span className="text-3xl font-bold">{pricingLabels["custom"]}</span>
        </div>
      ) : (
        ""
      )}

      {description ? (
        <div
          className={classNames(
            "subtitle mb-2 md:mb-5 text-base w-full",
            title == "Premium" ? "text-white" : "text-[#688092]"
          )}
        >
          {description}
        </div>
      ) : (
        ""
      )}

      <div className="feature-list flex flex-wrap gap-y-2">
        {features_list.map((feature: any) => (
          <div
            key={`feature-${feature}`}
            className="feture-list-item w-full flex align-center gap-x-2"
          >
            <img
              src={"/icons/check-mark.svg"}
              className="w-[20px] h-[20px]"
              alt="check-mark icon"
            />
            <span className="text-sm md:text-base leading-tight flex-1">
              {feature}
            </span>
          </div>
        ))}
      </div>

      <div className="free-space flex-1 w-full"></div>

      <div className="button-wrap mt-7 w-full">
        {buttonVisible && (
          <button
            data-testid="pricing-card-button"
            type="button"
            disabled={buttonDisable}
            className={classNames(
              "transition bg-white text-center justify-center flex items-center text-base leading-tight rounded-full pt-2.5 pb-2.5 pl-5 pr-5",
              title == SubscriptionPlan.FREE
                ? "bg-[#F1F4F6] text-[#085394] opacity-60"
                : "",
              title == SubscriptionPlan.PREMIUM
                ? "bg-[#F1F4F6] text-[#085394]"
                : "",
              title == SubscriptionPlan.ENTERPRISE
                ? "bg-[#0A6DC2] text-white"
                : ""
            )}
            onClick={handleClickButton}
          >
            {buttonText}
          </button>
        )}
      </div>
    </div>
  );
}

export default PricingCard;
