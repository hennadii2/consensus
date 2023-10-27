import classNames from "classnames";
import GraduationYearPicker from "components/GraduationYearPicker/GraduationYearPicker";
import Modal from "components/Modal";
import useLabels from "hooks/useLabels";
import React, { useCallback, useEffect, useState } from "react";

type GraduationYearModalProps = {
  open?: boolean;
  onClose: () => void;
  onSelect: (value: string) => void;
};

/**
 * @component GraduationYearModal
 * @description Component for asking graduation year
 * @example
 * return (
 *   <GraduationYearModal
 *    open={true}
 *    onClose={fn}
 *   />
 * )
 */
function GraduationYearModal({
  open,
  onClose,
  onSelect,
}: GraduationYearModalProps) {
  const [modalLabels] = useLabels("student-discount.ask-graduation-year-modal");
  const [selectedYear, setSelectedYear] = useState<string>("");

  const handleClickApply = useCallback(async () => {
    if (selectedYear == "") {
      return;
    }

    onClose();
    onSelect(selectedYear);
  }, [selectedYear, onClose, onSelect]);

  useEffect(() => {
    (async () => {
      if (open === true) {
        setSelectedYear("");
      }
    })();
    return () => {};
  }, [open, setSelectedYear]);

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
          data-testid="graduation-year-modal"
        >
          <img
            src={"/icons/x-blue.svg"}
            className="w-[24px] h-[24px] cursor-pointer absolute top-[20px] right-[20px] md:top-[32px] md:right-[32px]"
            onClick={onClose}
            alt="X"
          />

          <img
            src={"/icons/calendar.svg"}
            className="w-[80px] h-[80px] mx-auto"
            alt="Calendar"
          />

          <h3 className="text-[22px] text-center font-bold text-black mx-auto mt-[32px] md:mt-[40px]">
            {modalLabels["title"]}
          </h3>

          <div className="mt-8">
            <GraduationYearPicker
              value={selectedYear}
              onChange={(value: string) => {
                setSelectedYear(value);
              }}
            />
          </div>

          <div className="mt-8">
            <button
              data-testid="apply-button"
              type="button"
              className={classNames(
                "flex w-full text-[#085394] text-base justify-center items-center gap-x-3 rounded-full bg-[#D3EAFD] px-[26px] py-[10px]",
                selectedYear == "" ? "opacity-40" : ""
              )}
              onClick={handleClickApply}
            >
              {modalLabels["apply"]}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}

export default GraduationYearModal;
