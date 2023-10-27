import { useAuth } from "@clerk/nextjs";
import Modal from "components/Modal";
import {
  BOOKMARK_LISTNAME_FAVORITE,
  BOOKMARK_LISTNAME_MAX_LENGTH,
} from "constants/config";
import path from "constants/path";
import { createBookmarkListAPI } from "helpers/api";
import { IBookmarkCreateListResponse } from "helpers/bookmark";
import useLabels from "hooks/useLabels";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import { useRouter } from "next/router";
import React, { useCallback, useEffect, useRef, useState } from "react";
import { addBookmarkList } from "store/slices/bookmark";

type CreateNewListModalProps = {
  open?: boolean;
  onClose: (value: boolean) => void;
};

/**
 * @component CreateNewListModal
 * @description Component for save search modal
 * @example
 * return (
 *   <CreateNewListModal
 *    open={true}
 *    onClose={fn}
 *   />
 * )
 */
function CreateNewListModal({ open, onClose }: CreateNewListModalProps) {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const { isSignedIn, isLoaded } = useAuth();
  const [createNewListLabels] = useLabels("create-new-list-modal");
  const bookmarkLists = useAppSelector((state) => state.bookmark.bookmarkLists);
  const isLimitedBookmarkList = useAppSelector(
    (state) => state.bookmark.isLimitedBookmarkList
  );
  const isBookmarkListLoaded = useAppSelector(
    (state) => state.bookmark.isBookmarkListLoaded
  );

  const [newListInputValue, setNewListInputValue] = useState<string>("");
  const [isCreatingList, setIsCreatingList] = useState<Boolean>(false);
  const inputRef = useRef<any>(null);

  const handleClickCancel = useCallback(async () => {
    onClose(true);
  }, [onClose]);

  const handleClickCreateNewList = useCallback(async () => {
    if (!isLoaded) {
      router?.push(path.INTERNAL_SERVER_ERROR);
      return;
    }

    if (!isSignedIn) {
      router.push(
        `${path.SIGN_UP}#/?redirect_url=${encodeURIComponent(
          `${router?.asPath}`
        )}`
      );
      return;
    }

    if (newListInputValue.trim() == BOOKMARK_LISTNAME_FAVORITE) {
      return;
    }

    if (
      newListInputValue.trim().length > 0 &&
      isLimitedBookmarkList === false &&
      !isCreatingList
    ) {
      setIsCreatingList(true);
      try {
        const ret: IBookmarkCreateListResponse = await createBookmarkListAPI(
          newListInputValue.trim()
        );
        if (ret.success) {
          dispatch(addBookmarkList(ret.created_item));
          onClose(true);
        }
      } catch (error) {}
      setIsCreatingList(false);
    }
  }, [
    dispatch,
    router,
    isSignedIn,
    isLoaded,
    newListInputValue,
    isLimitedBookmarkList,
    isCreatingList,
    onClose,
  ]);

  const onChangeNewListLabel = async (e: any) => {
    setNewListInputValue(e.target.value);
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
        additionalClass={"mt-[60px]"}
      >
        <div
          className="p-12 bg-[url('/images/bg-card.webp')] bg-no-repeat bg-cover rounded-lg leading-none"
          data-testid="create-new-list-modal"
        >
          <div>
            <h3 className="text-2xl text-center font-bold text-black max-w-sm mx-auto">
              {createNewListLabels["title"]}
            </h3>
          </div>

          <div className="mt-9">
            <span className="block text-base text-[#303A40] ml-1">
              {createNewListLabels["list-name"]}
            </span>

            <div className="p-1 bg-white/50 rounded-lg mt-1">
              <input
                ref={inputRef}
                type="text"
                className="w-full border border-[#2AA3EF]/50 focus:border-[#2AA3EF]/50 hover:border-[#2AA3EF]/50 outline-none px-4 py-3 bg-white rounded-lg text-black"
                maxLength={BOOKMARK_LISTNAME_MAX_LENGTH}
                onChange={onChangeNewListLabel}
                onKeyUp={(e) => {
                  if (e.keyCode == 13) {
                    handleClickCreateNewList();
                  }
                }}
                enterKeyHint="go"
              />
            </div>

            <span className="block text-xs text-[#515A64] ml-1">
              {createNewListLabels["characters-maximum"].replace(
                "{max-value}",
                BOOKMARK_LISTNAME_MAX_LENGTH
              )}
            </span>
          </div>

          <div className="mt-9">
            <button
              onClick={handleClickCreateNewList}
              data-testid="button-save"
              className="flex w-full justify-center bg-[#0A6DC2] text-white py-2.5 rounded-full items-center cursor-pointer mt-4 disabled:opacity-60 disabled:cursor-not-allowed"
              disabled={Boolean(isCreatingList)}
            >
              <span>{createNewListLabels["button-create"]}</span>
            </button>

            <button
              onClick={handleClickCancel}
              data-testid="button-cancel"
              className="flex w-full justify-center bg-white border border-[#D6D2D6] text-white py-2.5 rounded-full items-center cursor-pointer mt-4"
            >
              <span className="text-[#000000]">
                {createNewListLabels["cancel"]}
              </span>
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}

export default CreateNewListModal;
