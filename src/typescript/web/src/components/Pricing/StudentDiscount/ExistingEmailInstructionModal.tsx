import Icon from "components/Icon";
import Modal from "components/Modal";
import { STUDENT_EMAIL } from "constants/config";
import useLabels from "hooks/useLabels";
import { useRouter } from "next/router";
import React from "react";

type ExistingEmailInstructionModalProps = {
  open?: boolean;
  onClose: () => void;
};

/**
 * @component ExistingEmailInstructionModal
 * @description Component for show existing email instructions
 * @example
 * return (
 *   <ExistingEmailInstructionModal
 *    open={true}
 *    onClose={fn}
 *   />
 * )
 */
function ExistingEmailInstructionModal({
  open,
  onClose,
}: ExistingEmailInstructionModalProps) {
  const router = useRouter();
  const [modalLabels] = useLabels("student-discount.existing-email-modal");

  const handleClickContact = (e: any) => {
    e.preventDefault();
    e.stopPropagation();
    window.location.href = "mailto:" + STUDENT_EMAIL;
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
          data-testid="existing-email-instruction-modal"
        >
          <img
            src={"/icons/x-blue.svg"}
            className="w-[24px] h-[24px] cursor-pointer absolute top-[20px] right-[20px] md:top-[32px] md:right-[32px]"
            onClick={onClose}
            alt="X"
          />

          <img
            src={"/icons/folder-info.svg"}
            className="w-[80px] h-[80px] mx-auto"
            alt="Folder"
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
              <span
                dangerouslySetInnerHTML={{ __html: modalLabels["description"] }}
                className="font-bold"
              ></span>
            </div>

            <div className="mt-3">
              <span className="font-bold mr-2">1.</span>
              <span
                dangerouslySetInnerHTML={{ __html: modalLabels["text1"] }}
                className=""
              ></span>
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
          </div>

          <div className="mt-8">
            <button
              data-testid="conatct-link-button"
              type="button"
              className="flex w-full text-[#085394] text-base justify-center items-center gap-x-3 rounded-full bg-[#D3EAFD] px-[26px] py-[10px]"
              onClick={handleClickContact}
            >
              <Icon size={20} name="mail" className="text-[#2AA3EF]" />
              {modalLabels["send-email"]}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}

export default ExistingEmailInstructionModal;
