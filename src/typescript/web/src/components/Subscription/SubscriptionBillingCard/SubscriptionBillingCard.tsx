import { PaymentDetailResponse } from "helpers/stripe";
import { UserSubscription } from "helpers/subscription";
import useLabels from "hooks/useLabels";
import React, { ReactNode } from "react";
import LoadingSubscriptionCard from "../LoadingSubscriptionCard/LoadingSubscriptionCard";

type Props = {
  children?: ReactNode;
  userSubscription: UserSubscription;
  paymentMethodDetail?: PaymentDetailResponse;
  isLoading?: boolean;
  onClick?: () => void;
};

/**
 * @component SubscriptionBillingCard
 * @description designed for subscription billing card
 * @example
 * return (
 *   <SubscriptionBillingCard>Learn more</SubscriptionBillingCard>
 * )
 */
const SubscriptionBillingCard = ({
  children,
  userSubscription,
  paymentMethodDetail,
  isLoading,
  onClick,
}: Props) => {
  const [billingLabels] = useLabels("billing-card");
  const dateOptions: Intl.DateTimeFormatOptions = {
    month: "long",
    day: "2-digit",
    year: "numeric",
  };
  const dateFormatPeriodEnd = new Date(
    userSubscription.current_period_end * 1000
  );

  if (isLoading) {
    return <LoadingSubscriptionCard />;
  }

  return (
    <>
      <div className="flex flex-wrap h-full flex-col">
        <div className="flex justify-between items-center w-full h-fit">
          <h4 className="text-[#222F2B] font-bold text-lg">
            {billingLabels["title"]}
          </h4>

          <button
            data-testid="manage-payment-method-button"
            type="button"
            className="text-base text-[#0A6DC2] font-bold"
            onClick={onClick}
          >
            {billingLabels["manage-payment-method"]}
          </button>
        </div>

        {paymentMethodDetail && paymentMethodDetail.type == "card" && (
          <div
            data-testid="billing-card-detail"
            className="flex flex-wrap w-full h-fit items-center mt-8 text-[#354B44] text-base"
          >
            <img
              className="w-[44px] h-[28px]"
              src={`/images/payment_methods/${paymentMethodDetail.card.brand.toLowerCase()}.png`}
              alt={paymentMethodDetail.card.brand}
            />

            <span className="ml-2">
              **** {paymentMethodDetail.card.last4} {billingLabels["expiring"]}{" "}
              {paymentMethodDetail.card.exp_month}/
              {paymentMethodDetail.card.exp_year}
            </span>
          </div>
        )}

        <div className="flex-1"></div>
        <div
          data-testid="renews-date"
          className="text-[#222F2B] text-sm w-full flex flex-1 height-auto items-end mt-8"
        >
          <span className="mr-1">{billingLabels["renews-on"]}</span>
          <span className="font-bold">
            {dateFormatPeriodEnd.toLocaleString("en-US", dateOptions)}
          </span>
        </div>
      </div>
    </>
  );
};

export default SubscriptionBillingCard;
