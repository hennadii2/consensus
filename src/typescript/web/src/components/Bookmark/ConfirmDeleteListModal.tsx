import Modal from "components/Modal";
import useLabels from "hooks/useLabels";
import { useRouter } from "next/router";
import React, { useCallback } from "react";

type ConfirmDeleteListModalProps = {
  open?: boolean;
  onClose: (value: boolean) => void;
};

/**
 * @component ConfirmDeleteListModal
 * @description Component for confirm delete list modal
 * @example
 * return (
 *   <ConfirmDeleteListModal
 *    open={true}
 *    onClose={fn}
 *   />
 * )
 */
function ConfirmDeleteListModal({
  open,
  onClose,
}: ConfirmDeleteListModalProps) {
  const router = useRouter();
  const [modalLabels] = useLabels("confirm-bookmark-list-modal");

  const handleClickConfirm = useCallback(async () => {
    onClose(true);
  }, [onClose]);

  const handleClickCancel = useCallback(async () => {
    onClose(false);
  }, [onClose]);

  return (
    <>
      <Modal
        open={open}
        onClose={handleClickCancel}
        size="md"
        padding={false}
        mobileFit={true}
        additionalClass={"mt-[60px]"}
      >
        <div
          className="p-12 bg-[url('/images/bg-card.webp')] bg-no-repeat bg-cover rounded-lg leading-none"
          data-testid="cofirm-delete-list-modal"
        >
          <img
            alt="delete"
            src={`/icons/delete-file.svg`}
            className="w-[75px] h-[75px] mx-auto"
          />

          <div>
            <h3 className="text-[22px] text-center font-bold text-black max-w-sm mx-auto mt-[40px]">
              {modalLabels["title"]}
            </h3>
          </div>

          <div className="mt-4">
            <span className="block text-base text-black">
              {modalLabels["description"]}
            </span>
          </div>

          <div className="mt-9">
            <button
              onClick={handleClickCancel}
              data-testid="button-cancel"
              className="flex w-full justify-center bg-[#D3EAFD] py-2.5 rounded-full items-center cursor-pointer mt-4"
            >
              <span className="text-[#085394]">
                {modalLabels["button-cancel"]}
              </span>
            </button>

            <button
              onClick={handleClickConfirm}
              data-testid="button-save"
              className="flex w-full justify-center bg-white border border-[#D6D2D6] text-[#C6211F] py-2.5 rounded-full items-center cursor-pointer mt-4"
            >
              <span>{modalLabels["button-ok"]}</span>
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}

export default ConfirmDeleteListModal;
