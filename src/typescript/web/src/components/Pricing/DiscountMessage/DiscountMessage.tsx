import Icon from "components/Icon";
import useLabels from "hooks/useLabels";
import React, { useRef, useState } from "react";

type DiscountMessageProps = {
  onClickVerifyAccount: () => void;
  onClickShowInstructionToMergeAccount: () => void;
  onClickShowExistingEmailInstruction: () => void;
};

function DiscountMessage({
  onClickVerifyAccount,
  onClickShowInstructionToMergeAccount,
  onClickShowExistingEmailInstruction,
}: DiscountMessageProps) {
  const [expand, setExpand] = useState(false);
  const [pageLabels] = useLabels("screens.pricing");
  const ref = useRef<HTMLDivElement>(null);

  const handleClickVerifyAccount = (e: any) => {
    e.preventDefault();
    e.stopPropagation();
    onClickVerifyAccount();
  };

  const handleClickMergeAccount = (e: any) => {
    e.preventDefault();
    e.stopPropagation();
    onClickShowInstructionToMergeAccount();
  };

  const handleClickExistingEmail = (e: any) => {
    e.preventDefault();
    e.stopPropagation();
    onClickShowExistingEmailInstruction();
  };

  return (
    <div
      onClick={() => setExpand(!expand)}
      data-testid="discount-message"
      className="cursor-pointer bg-white p-6 md:p-8 rounded-2xl"
      style={{
        boxShadow: "4px 10px 16px 0px rgba(189, 201, 219, 0.16)",
      }}
    >
      <div className="flex justify-between items-center">
        <div className="flex">
          <img
            alt="discount"
            src="/icons/discount.svg"
            className="w-[24px] h-[24px]"
          />
          <h4 className="font-bold text-lg ml-2 text-black">
            {pageLabels["discount-title"]}
          </h4>
        </div>
        {expand ? (
          <Icon size={18} name="minus" />
        ) : (
          <Icon size={18} name="plus" />
        )}
      </div>
      <div
        style={{
          height: expand
            ? ref.current?.clientHeight
              ? ref.current?.clientHeight + 24
              : "auto"
            : 0,
          transition: ".2s",
          overflow: "hidden",
        }}
      >
        <div className="text-sm" ref={ref}>
          <div className="">
            <h5 className="text-[#222F2B] text-sm mt-[24px]">
              {pageLabels["discount-message-title"]}
            </h5>

            <div
              className="px-[16px] py-[20px] rounded-xl border border-[#DEE0E3] mt-[16px] flex items-center"
              onClick={handleClickVerifyAccount}
            >
              <img
                alt="email-check"
                src="/icons/email-check.svg"
                className="w-[24px] h-[24px]"
              />
              <span className="text-[#364B44] text-base ml-[12px]">
                {pageLabels["discount-message-text1"]}
              </span>
            </div>

            <div
              className="px-[16px] py-[20px] rounded-xl border border-[#DEE0E3] mt-[12px] flex items-center"
              onClick={handleClickMergeAccount}
            >
              <img
                alt="email-plus"
                src="/icons/email-plus.svg"
                className="w-[24px] h-[24px]"
              />
              <span className="text-[#364B44] text-base ml-[12px]">
                {pageLabels["discount-message-text2"]}
              </span>
            </div>

            <div
              className="px-[16px] py-[20px] rounded-xl border border-[#DEE0E3] mt-[12px] flex items-center"
              onClick={handleClickExistingEmail}
            >
              <img
                alt="email-minus"
                src="/icons/email-minus.svg"
                className="w-[24px] h-[24px]"
              />
              <span className="text-[#364B44] text-base ml-[12px]">
                {pageLabels["discount-message-text3"]}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DiscountMessage;
