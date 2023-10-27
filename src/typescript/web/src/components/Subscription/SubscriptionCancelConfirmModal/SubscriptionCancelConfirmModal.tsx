import Modal from "components/Modal";
import { SALES_EMAIL, SUPPORT_EMAIL } from "constants/config";
import { getFeatureCopyList, getPremiumProduct } from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React from "react";

type SubscriptionCancelConfirmModalProps = {
  open?: boolean;
  onClose: (value: boolean) => void;
  onClickButton?: () => void;
  onClickCancel?: () => void;
};

/**
 * @component SubscriptionCancelConfirmModal
 * @description Component for subscription cancel confirm modal
 * @example
 * return (
 *   <SubscriptionCancelConfirmModal
 *    open={true}
 *    onClick={fn}
 *    title="Confirm"
 *    text="Hello"
 *   />
 * )
 */
function SubscriptionCancelConfirmModal({
  onClose,
  open,
  onClickButton,
  onClickCancel,
}: SubscriptionCancelConfirmModalProps) {
  const [pageLabels] = useLabels("screens.subscription");
  const [subscriptionFeaturesLabels] = useLabels("subscription-features");
  const products = useAppSelector((state) => state.subscription.products);
  const premiumProduct = getPremiumProduct(products);
  const features_list = getFeatureCopyList(premiumProduct);

  const handleClickContact = () => {
    window.location.href = "mailto:" + SALES_EMAIL;
  };

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
      <Modal open={open} onClose={onClose} size="xl" padding={false}>
        <div
          className="p-12 bg-[url('/images/bg-card.webp')] bg-cover bg-no-repeat leading-tight text-[#303A40]"
          data-testid="confirm-cancel-subscription-modal"
        >
          <div className="text-center">
            <img
              src={"/icons/envelope-sad.svg"}
              className="inline-block w-[80px] h-[80px]"
              alt="envelope-sad icon"
            />
            <h3 className="text-[22px] text-center font-bold max-w-full mx-auto mt-10">
              {pageLabels["cancel-confirm-modal"]["title"]}
            </h3>
          </div>

          <div className="text-center rounded-md bg-white mt-8 pl-2 pr-2 pt-6 pb-6">
            <div className="max-w-[250px] inline-block">
              <p className="text-base">
                {pageLabels["cancel-confirm-modal"]["title-lose-access"]}
              </p>

              <div
                data-testid="feature-list"
                className="flex flex-wrap gap-y-3 mt-4"
              >
                {features_list.map((feature: any) => (
                  <div
                    key={`feature-${feature}`}
                    className="feture-list-item w-full flex items-center gap-x-2"
                  >
                    <img
                      src={"/icons/minus-red-rounded.svg"}
                      className="w-[20px] h-[20px]"
                      alt="minus icon"
                    />
                    <span className="text-left text-sm leading-tight flex-1">
                      {feature}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-10 text-base text-center">
            {pageLabels["cancel-confirm-modal"]["text1"]}
          </div>
          <div className="mt-5 text-base text-center">
            {pageLabels["cancel-confirm-modal"]["text2"]}
          </div>
          <div className="text-center">
            <button
              data-testid="conatct-link-button"
              type="button"
              className="inline-block text-[#0A6DC2] text-base font-bold"
              onClick={handleClickContact}
            >
              {SUPPORT_EMAIL}
            </button>
          </div>

          <div className="mt-10">
            <button
              onClick={handleClickCancel}
              className="flex w-full justify-center bg-[#0A6DC2] text-white py-3 rounded-full items-center cursor-pointer"
            >
              {pageLabels["cancel-confirm-modal"]["confirm"]}
            </button>

            <button
              onClick={handleClickConfirm}
              className="flex w-full justify-center bg-[#D3EAFD] text-[#085394] mt-4 py-3 rounded-full items-center cursor-pointer"
            >
              {pageLabels["cancel-confirm-modal"]["cancel"]}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}

export default SubscriptionCancelConfirmModal;
