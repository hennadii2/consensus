import { Dialog, Transition } from "@headlessui/react";
import classNames from "classnames";
import { useAppSelector } from "hooks/useStore";
import React, { Fragment, useEffect, useRef } from "react";

type ModalProps = {
  open?: boolean;
  title?: string;
  text?: string;
  children?: React.ReactNode;
  onClose: (value: boolean) => void;
  size?: "md" | "lg" | "xl";
  padding?: boolean;
  overflowVisible?: boolean;
  mobileFit?: boolean;
  additionalClass?: string;
};

/**
 * @component Modal
 * @description Component for share modal
 * @example
 * return (
 *   <Modal
 *    open={true}
 *    onClick={fn}
 *    title="Share"
 *    text="Hello"
 *   />
 * )
 */
function Modal({
  onClose,
  open,
  title,
  text,
  children,
  size,
  padding = true,
  overflowVisible,
  mobileFit,
  additionalClass,
}: ModalProps) {
  // Fix for scroll freezing, see: https://github.com/tailwindlabs/headlessui/issues/1199
  useEffect(() => {
    if (!open) {
      document.documentElement.style.overflow = "auto";
    }
  }, [open]);
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  let refDiv = useRef(null);

  return (
    <>
      <Transition appear show={open} as={Fragment}>
        <Dialog
          as="div"
          open={open}
          className="relative z-[9999999999]"
          onClose={onClose}
          static
          initialFocus={refDiv}
        >
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-60" />
          </Transition.Child>

          <div data-testid="modal" className="fixed inset-0 overflow-y-auto">
            <div
              className={classNames(
                "flex min-h-full justify-center text-center",
                mobileFit && isMobile ? "items-end" : "items-center",
                mobileFit && isMobile ? "p-0" : "p-4"
              )}
            >
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel
                  className={classNames(
                    "w-full transform rounded-lg bg-white  text-left align-middle shadow-xl transition-all",
                    overflowVisible ? "overflow-visible" : "overflow-hidden",
                    size === "xl"
                      ? "max-w-xl"
                      : size === "lg"
                      ? "max-w-lg"
                      : "max-w-md",
                    padding ? "p-6" : "",
                    additionalClass ? additionalClass : ""
                  )}
                >
                  <Dialog.Title
                    as="h3"
                    className="text-2xl font-semibold leading-6 text-gray-700"
                  >
                    {title}
                  </Dialog.Title>
                  <div ref={refDiv}>
                    {text && (
                      <div className="mt-3">
                        <p className="text-lg text-gray-900">{text}</p>
                      </div>
                    )}
                    {children}
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </>
  );
}

export default Modal;
