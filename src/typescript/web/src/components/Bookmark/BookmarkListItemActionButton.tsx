import { Popover, Transition } from "@headlessui/react";
import useLabels from "hooks/useLabels";
import React, { Fragment } from "react";

interface BookmarkListItemActionButtonProps {
  onClickEditList?: () => void;
  onClickDeleteList?: () => void;
}

function BookmarkListItemActionButton({
  onClickEditList,
  onClickDeleteList,
}: BookmarkListItemActionButtonProps) {
  const [actionButtonLabels] = useLabels(
    "screens.bookmark-lists.action-button"
  );

  return (
    <Popover>
      {({ close }: any) => (
        <div className="relative inline-flex items-center h-full">
          <Popover.Button data-testid="more-button" className="p-[10px]">
            <img
              src={"/icons/more-vertical.svg"}
              className="w-[20px] h-[20px]"
              alt="more icon"
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
              className={`absolute right-0 z-10 min-w-[260px] rounded-2xl bg-white top-10 shadow-[-3px_4px_26px_rgba(115,121,119,0.25)]
              }`}
            >
              <div data-testid="action-content" className="pt-2 pb-2 text-sm">
                <button
                  className="flex relative items-center py-2 hover:bg-[#F8F9FC] cursor-pointer px-6 w-full"
                  onClick={(e: any) => {
                    e.preventDefault();
                    e.stopPropagation();
                    if (onClickEditList) {
                      onClickEditList();
                    }
                  }}
                >
                  <div className="w-[24px] h-[24px] mr-3 flex items-center justify-center">
                    <img alt="edit" src={`/icons/edit.svg`} />
                  </div>
                  <div>
                    <p className="font-medium text-sm">
                      {actionButtonLabels["edit-list"]}
                    </p>
                  </div>
                </button>
                <button
                  className="flex relative items-center py-2 hover:bg-[#F8F9FC] cursor-pointer px-6 w-full"
                  onClick={(e: any) => {
                    e.preventDefault();
                    e.stopPropagation();
                    if (onClickDeleteList) {
                      onClickDeleteList();
                    }
                  }}
                >
                  <div className="w-[24px] h-[24px] mr-3 flex items-center justify-center">
                    <img alt="trash" src={`/icons/trash-red.svg`} />
                  </div>
                  <div>
                    <p className="font-medium text-sm">
                      {actionButtonLabels["delete-list"]}
                    </p>
                  </div>
                </button>
              </div>
            </Popover.Panel>
          </Transition>
        </div>
      )}
    </Popover>
  );
}

export default BookmarkListItemActionButton;
