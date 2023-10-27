import Modal from "components/Modal";
import { roundDownSignificantDigits } from "helpers/format";
import {
  getReversedSubscriptionUsageData,
  isSubscriptionCanceledNotExpired,
} from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React from "react";

type SubscriptionResumeConfirmModalProps = {
  open?: boolean;
  onClose: (value: boolean) => void;
  onClickButton?: () => void;
  onClickCancel?: () => void;
};

/**
 * @component SubscriptionResumeConfirmModal
 * @description Component for subscription resume confirm modal
 * @example
 * return (
 *   <SubscriptionResumeConfirmModal
 *    open={true}
 *    onClick={fn}
 *    title="Confirm"
 *    text="Hello"
 *   />
 * )
 */
function SubscriptionResumeConfirmModal({
  onClose,
  open,
  onClickButton,
  onClickCancel,
}: SubscriptionResumeConfirmModalProps) {
  const [pageLabels] = useLabels("screens.subscription");
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

  const subscription: any = useAppSelector(
    (state) => state.subscription.subscription
  );
  const subscriptionUsageData = useAppSelector(
    (state) => state.subscription.usageData
  );
  const reversedSubscriptionUsageData = getReversedSubscriptionUsageData(
    subscriptionUsageData
  );
  const subscriptionInterval =
    subscription.user && subscription.user.plan.interval == "year"
      ? "year"
      : "month";
  let unitAmount = subscription.user
    ? subscription.user.plan.amount_decimal
    : 0;

  if (
    subscription?.user &&
    subscription?.user.discount &&
    subscription?.user.discount.coupon
  ) {
    if (
      subscription?.user.discount.coupon.valid &&
      subscription?.user.discount.coupon.percent_off
    ) {
      unitAmount =
        (unitAmount * (100 - subscription?.user.discount.coupon.percent_off)) /
        100;
    }
  }

  let expireDate = null;
  if (
    subscription?.user &&
    isSubscriptionCanceledNotExpired(subscription?.user)
  ) {
    expireDate = new Date(subscription?.user.cancel_at * 1000);
  }

  const handleClickConfirm = () => {
    onClose(true);
    onClickButton?.();
  };

  const handleClickCancel = () => {
    onClose(true);
    onClickCancel?.();
  };

  return (
    <>
      <Modal open={open} onClose={onClose} size="md" padding={false}>
        <div
          className="p-12 bg-[url('/images/bg-card.webp')] bg-cover bg-no-repeat leading-tight text-[#303A40]"
          data-testid="confirm-resume-subscription-modal"
        >
          <div className="text-center">
            <img
              src={"/icons/premium.svg"}
              className="inline-block w-[80px] h-[80px]"
              alt="premium icon"
            />
            <h3 className="text-[22px] text-[#364B44] text-center font-bold max-w-full mx-auto mt-[40px]">
              {pageLabels["resume-confirm-modal"]["title"]}
            </h3>
          </div>

          <div className="mt-[12px] text-center">
            <span
              data-testid="subscription-unit-amount"
              className="text-[#222F2B] text-4xl font-bold"
            >
              {currencyFormatter.format(
                Number(
                  roundDownSignificantDigits(unitAmount / 100, 4).toFixed(2)
                )
              )}
            </span>
            <span
              data-testid="subscription-interval"
              className="text-[#688092] text-base ml-1"
            >
              {"/per "}
              {subscriptionInterval}
            </span>
          </div>

          {expireDate && (
            <div className="mt-[8px] text-sm text-center">
              <span className="mr-1 text-[#364B44]">
                {pageLabels["resume-confirm-modal"]["renews-on"]}
              </span>
              <span className="font-bold text-[#222F2B]">
                {expireDate.toLocaleDateString("en-US", dateOptions)}
              </span>
            </div>
          )}

          <div className="mt-[40px]">
            <button
              onClick={handleClickConfirm}
              className="flex w-full justify-center bg-[#0A6DC2] text-white py-3 rounded-full items-center cursor-pointer"
            >
              {pageLabels["resume-confirm-modal"]["button-yes"]}
            </button>

            <button
              onClick={handleClickCancel}
              className="flex w-full justify-center bg-[#D3EAFD] text-[#085394] mt-4 py-3 rounded-full items-center cursor-pointer"
            >
              {pageLabels["resume-confirm-modal"]["button-cancel"]}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}

export default SubscriptionResumeConfirmModal;
