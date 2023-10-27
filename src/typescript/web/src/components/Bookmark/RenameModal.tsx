import classNames from "classnames";
import Modal from "components/Modal";
import { BOOKMARK_LISTNAME_MAX_LENGTH } from "constants/config";
import React, { useCallback, useEffect, useRef, useState } from "react";

type RenameModalProps = {
  open?: boolean;
  onClose: (value: boolean, newLabel?: string) => void;
  initialLabel: string;
};

/**
 * @component RenameModal
 * @description Component for rename modal
 * @example
 * return (
 *   <RenameModal
 *    open={true}
 *    onClose={fn}
 *    initialLabel=""
 *   />
 * )
 */
function RenameModal({ open, onClose, initialLabel }: RenameModalProps) {
  const [newInputValue, setNewInputValue] = useState<string>(initialLabel);
  const inputRef = useRef<any>(null);

  useEffect(() => {
    setNewInputValue(initialLabel);
  }, [initialLabel, setNewInputValue]);

  const handleClickCancel = useCallback(async () => {
    onClose(false);
    setNewInputValue(initialLabel);
  }, [onClose, setNewInputValue, initialLabel]);

  const handleClickConfirm = useCallback(async () => {
    onClose(true, newInputValue);
  }, [newInputValue, onClose]);

  const onChangeNewLabel = async (e: any) => {
    setNewInputValue(e.target.value);
  };

  useEffect(() => {
    if (open) {
      setTimeout(() => {
        if (inputRef && inputRef.current) {
          inputRef.current.focus();
        }
      }, 500);
    }
  }, [open, inputRef]);

  return (
    <>
      <Modal
        open={open}
        onClose={handleClickCancel}
        size="md"
        padding={false}
        mobileFit={true}
        additionalClass={"rounded-none !max-w-full fixed bottom-0 pb-[10px]"}
      >
        <div className="leading-none" data-testid="rename-modal">
          <div className={classNames("px-4 pt-3 pb-4 flex")}>
            <input
              ref={inputRef}
              type="text"
              className="bg-transparent flex-1 outline-none text-ellipsis text-lg w-full pr-[10px]"
              value={newInputValue}
              maxLength={BOOKMARK_LISTNAME_MAX_LENGTH}
              onChange={onChangeNewLabel}
              onKeyUp={(e) => {
                if (e.keyCode == 13) {
                  handleClickConfirm();
                }
              }}
              enterKeyHint="go"
            />

            <div className="flex items-center">
              <img
                src={"/icons/x-gray.svg"}
                className="w-[20px] h-[20px] cursor-pointer"
                alt="x icon"
                onClick={handleClickCancel}
              />

              <img
                src={"/icons/check2-green.svg"}
                className="w-[20px] h-[20px] cursor-pointer ml-3"
                alt="check2 icon"
                onClick={handleClickConfirm}
              />
            </div>
          </div>
        </div>
      </Modal>
    </>
  );
}

export default RenameModal;
