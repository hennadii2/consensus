import { Dialog, Transition } from "@headlessui/react";
import { Fragment } from "react";

type DrawerProps = {
  open?: boolean;
  title?: string;
  children?: React.ReactNode;
  onClose: (value: boolean) => void;
};

function Drawer({ open, onClose, children, title }: DrawerProps) {
  return (
    <Transition.Root show={open} as={Fragment}>
      <Dialog as="div" className="relative z-[2147483004]" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-in-out duration-500"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in-out duration-500"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-[#20202066] sm:bg-transparent transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-hidden">
          <div className="absolute inset-0 overflow-hidden">
            <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pt-[70px] sm:pt-0">
              <Transition.Child
                as={Fragment}
                enter="transform transition ease-in-out duration-500 sm:duration-700"
                enterFrom="translate-y-full sm:translate-x-full sm:translate-y-0"
                enterTo="translate-y-0 sm:translate-x-0 sm:translate-y-0"
                leave="transform transition ease-in-out duration-500 sm:duration-700"
                leaveFrom="translate-y-0 sm:translate-x-0 sm:translate-y-0"
                leaveTo="translate-y-full sm:translate-x-full sm:translate-y-0"
              >
                <Dialog.Panel className="pointer-events-auto relative w-screen sm:max-w-[322px]">
                  <div
                    data-testid="drawer"
                    className="flex h-full flex-col overflow-y-scroll bg-white pt-[26px] sm:pt-8 shadow-xl  rounded-t-[20px] sm:rounded-none"
                  >
                    <div className="flex flex-row justify-between items-center px-[21px] sm:px-[26px]">
                      <Dialog.Title className="text-[22px] text-[#364B44] font-bold leading-8 tracking-[0.22px]">
                        {title}
                      </Dialog.Title>
                      <button
                        type="button"
                        className="w-5 h-5 sm:w-6 sm:h-6"
                        onClick={() => onClose(false)}
                      >
                        <img
                          src={"/icons/x-gray.svg"}
                          className="w-5 h-5 sm:w-6 sm:h-6 cursor-pointer"
                          alt="x icon"
                        />
                      </button>
                    </div>
                    <div className="relative mt-[26px] flex-1 overflow-y-auto px-[21px] sm:px-[26px]">
                      {children}
                    </div>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
}

export default Drawer;
