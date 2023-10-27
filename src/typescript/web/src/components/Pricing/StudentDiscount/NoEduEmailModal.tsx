import Modal from "components/Modal";
import path from "constants/path";
import useLabels from "hooks/useLabels";
import Link from "next/link";
import { useRouter } from "next/router";
import React from "react";

type NoEduEmailModalProps = {
  open?: boolean;
  onClose: () => void;
};

/**
 * @component NoEduEmailModal
 * @description Component for show no edu email modal
 * @example
 * return (
 *   <NoEduEmailModal
 *    open={true}
 *    onClose={fn}
 *   />
 * )
 */
function NoEduEmailModal({ open, onClose }: NoEduEmailModalProps) {
  const router = useRouter();
  const [modalLabels] = useLabels("student-discount.no-edu-email-modal");

  const handleClickSupport = (e: any) => {
    e.preventDefault();
    e.stopPropagation();

    if (window && window.Intercom) {
      window.Intercom("show");
    }

    if (onClose) {
      onClose();
    }
  };

  return (
    <>
      <Modal
        open={open}
        onClose={onClose}
        size="md"
        padding={false}
        mobileFit={true}
        additionalClass={"mt-[0px] max-w-[565px]"}
      >
        <div
          className="px-[20px] py-[40px] md:py-[60px] md:px-[60px] bg-[url('/images/bg-card.webp')] bg-no-repeat bg-cover rounded-lg leading-none"
          data-testid="no-edu-email-modal"
        >
          <img
            src={"/icons/x-blue.svg"}
            className="w-[24px] h-[24px] cursor-pointer absolute top-[20px] right-[20px] md:top-[32px] md:right-[32px]"
            onClick={onClose}
            alt="X"
          />

          <img
            src={"/icons/email-close.svg"}
            className="w-[80px] h-[80px] mx-auto"
            alt="Email"
          />

          <h3 className="text-[22px] text-center font-bold text-black mx-auto mt-[32px] md:mt-[40px]">
            {modalLabels["title"]}
          </h3>

          <div className="text-center text-base font-normal mt-4 text-black">
            <span className="mr-1">{modalLabels["text1"]}</span>
            <Link href={path.ACCOUNT} legacyBehavior>
              <a className="font-bold text-[#0A6DC2]">
                {modalLabels["link-text1"]}
              </a>
            </Link>
            <span className="mr-1">{modalLabels["text2"]}</span>
            <span
              className="font-bold text-[#0A6DC2] cursor-pointer mr-1"
              onClick={handleClickSupport}
            >
              {modalLabels["link-text2"]}
            </span>
            <span className="">{modalLabels["text3"]}</span>
          </div>
        </div>
      </Modal>
    </>
  );
}

export default NoEduEmailModal;
