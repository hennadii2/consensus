import Modal from "components/Modal";
import path from "constants/path";
import useLabels from "hooks/useLabels";
import Link from "next/link";
import { useRouter } from "next/router";
import React from "react";

type MergeAccountModalProps = {
  open?: boolean;
  onClose: () => void;
};

/**
 * @component MergeAccountModal
 * @description Component for show instructions to merge account
 * @example
 * return (
 *   <MergeAccountModal
 *    open={true}
 *    onClose={fn}
 *   />
 * )
 */
function MergeAccountModal({ open, onClose }: MergeAccountModalProps) {
  const router = useRouter();
  const [modalLabels] = useLabels("student-discount.merge-account-modal");

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
          data-testid="merge-account-modal"
        >
          <img
            src={"/icons/x-blue.svg"}
            className="w-[24px] h-[24px] cursor-pointer absolute top-[20px] right-[20px] md:top-[32px] md:right-[32px]"
            onClick={onClose}
            alt="X"
          />

          <img
            src={"/icons/file-info.svg"}
            className="w-[80px] h-[80px] mx-auto"
            alt="File"
          />

          <h3 className="text-[22px] text-center font-bold text-black mx-auto mt-[32px] md:mt-[40px]">
            {modalLabels["title"]}
          </h3>

          <div
            style={{
              boxShadow: "-4px 6px 25px 0px rgba(189, 201, 219, 0.20)",
            }}
            className="mt-[32px] bg-white p-[24px] rounded-[12px] text-black text-[14px] leading-snug"
          >
            <div>
              <span className="font-bold mr-2">1.</span>
              <span
                dangerouslySetInnerHTML={{ __html: modalLabels["text1"] }}
                className="mr-1"
              ></span>
              <Link href={path.ACCOUNT} legacyBehavior>
                <a className="font-bold text-[#0A6DC2]">
                  {modalLabels["text1-link-text"]}
                </a>
              </Link>
            </div>

            <div className="mt-3">
              <span className="font-bold mr-2">2.</span>
              <span
                dangerouslySetInnerHTML={{ __html: modalLabels["text2"] }}
                className=""
              ></span>
            </div>

            <div className="mt-3">
              <span className="font-bold mr-2">3.</span>
              <span
                dangerouslySetInnerHTML={{ __html: modalLabels["text3"] }}
                className=""
              ></span>
            </div>

            <div className="mt-3">
              <span className="font-bold mr-2">4.</span>
              <span
                dangerouslySetInnerHTML={{ __html: modalLabels["text4"] }}
                className=""
              ></span>
            </div>
          </div>
        </div>
      </Modal>
    </>
  );
}

export default MergeAccountModal;
