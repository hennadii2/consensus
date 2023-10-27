import { Popover, Transition } from "@headlessui/react";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React, { Fragment, useRef } from "react";

type BetaTagProps = {
  text?: boolean;
};

/**
 * @component BetaTag
 * @description Component Beta Tag.
 * @example
 * return (
 *   <BetaTag />
 * )
 */
const BetaTag = ({ text }: BetaTagProps) => {
  const [betaLabels] = useLabels("beta");
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  const buttonRef = useRef<HTMLButtonElement | null>(null);
  const timeoutDuration = 200;
  let timeout: any;

  const closePopover = () => {
    return buttonRef.current?.dispatchEvent(
      new KeyboardEvent("keydown", {
        key: "Escape",
        bubbles: true,
        cancelable: true,
      })
    );
  };

  const onMouseEnter = (open: boolean) => {
    if (!isMobile) {
      clearTimeout(timeout);
      if (open) return;
      return buttonRef.current?.click();
    }
  };

  const onMouseLeave = (open: boolean) => {
    if (!isMobile) {
      if (!open) return;
      timeout = setTimeout(() => closePopover(), timeoutDuration);
    }
  };

  return (
    <span
      data-testid="beta-tag"
      className={`border-[#57AC91] border  rounded-full flex justify-center items-center gap-[6px] ${
        text
          ? "text-white bg-[#57AC91] text-xs font-bold md:leading-[18px] leading-[14.56px] py-[6px] px-2"
          : "text-xs md:text-sm h-[24px] md:h-[31px] px-2.5 md:px-3.5 text-[#57AC91]"
      }`}
    >
      beta
      {text && (
        <Popover>
          {({ open }) => (
            <div>
              <Popover.Button
                className="flex outline-none"
                ref={buttonRef}
                onMouseEnter={onMouseEnter.bind(null, open)}
                onMouseLeave={onMouseLeave.bind(null, open)}
              >
                <img
                  data-testid="beta-tag-text"
                  alt="Beta info"
                  src="/icons/white-info.svg"
                />
              </Popover.Button>
              <Transition
                as={Fragment}
                enter="transition ease-out duration-200"
                enterFrom="opacity-0 translate-y-1"
                enterTo="opacity-100 translate-y-0"
                leave="transition ease-in duration-150"
                leaveFrom="opacity-100 translate-y-0"
                leaveTo="opacity-0 translate-y-1"
              >
                <Popover.Panel
                  className={`absolute left-0 z-10 w-[280px] sm:w-[350px] bg-white shadow-lg rounded-md top-11`}
                >
                  <div data-testid="beta-content" className="py-4 px-4 text-sm">
                    <div
                      className={`bg-white absolute h-3 w-3 -top-1 rotate-45 left-[45px]`}
                    ></div>
                    <p className="text-green-600 font-normal">
                      <span className="font-bold mr-1">
                        {betaLabels["important-note"]}
                      </span>
                      {betaLabels["first-text"]}
                    </p>
                    <p className="text-green-600 mt-2 font-normal">
                      {betaLabels["second-text"]}
                    </p>
                  </div>
                </Popover.Panel>
              </Transition>
            </div>
          )}
        </Popover>
      )}
    </span>
  );
};

export default BetaTag;
