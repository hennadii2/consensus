import classNames from "classnames";
import VerticalDivider from "components/VerticalDivider";
import {
  BOOKMARK_LISTNAME_FAVORITE,
  BOOKMARK_LISTNAME_MAX_LENGTH,
} from "constants/config";
import { updateBookmarkListAPI } from "helpers/api";
import {
  getPaperSearchNum,
  IBookmarkListItem,
  IBookmarkUpdateListResponse,
} from "helpers/bookmark";
import { bookmarkListDetailPagePath } from "helpers/pageUrl";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import { useRouter } from "next/router";
import React, { ReactNode, useCallback, useRef, useState } from "react";
import { updateBookmarkList } from "store/slices/bookmark";
import BookmarkListItemActionButton from "./BookmarkListItemActionButton";
import RenameModal from "./RenameModal";

type Props = {
  children?: ReactNode;
  bookmarkList: IBookmarkListItem;
  onClickEditList?: () => void;
  onClickDeleteList?: () => void;
};

/**
 * @component BookmarkListItem
 * @description designed for bookmark list item
 * @example
 * return (
 *   <BookmarkListItem onClick={fn}>Learn more</ClaimButton>
 * )
 */
const BookmarkListItem = ({
  children,
  bookmarkList,
  onClickEditList,
  onClickDeleteList,
}: Props) => {
  const dispatch = useAppDispatch();
  const router = useRouter();
  const inputRef = useRef<any>(null);
  const isMobile = useAppSelector((state) => state.setting.isMobile);
  const bookmarkItems = useAppSelector((state) => state.bookmark.bookmarkItems);
  const [isEditMode, setIsEditMode] = useState(false);
  const [currentEditText, setCurrentEditText] = useState<string>("");
  const { paperNum, searchNum } = getPaperSearchNum(
    bookmarkList.id,
    bookmarkItems
  );
  const [openRenameModal, setOpenRenameModal] = useState(false);
  const isFavorite = bookmarkList.text_label == BOOKMARK_LISTNAME_FAVORITE;

  const handleClickEditList = useCallback(async () => {
    if (isMobile) {
      setCurrentEditText(bookmarkList.text_label);
      setOpenRenameModal(true);
    } else {
      setCurrentEditText(bookmarkList.text_label);
      setIsEditMode(true);
    }
    if (inputRef && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isMobile, bookmarkList, setIsEditMode, setCurrentEditText]);

  const handleClickCancelEdit = useCallback(async () => {
    setIsEditMode(false);
    setCurrentEditText("");
  }, [setIsEditMode, setCurrentEditText]);

  const handleClickConfirmEdit = useCallback(
    async (label?: string) => {
      let newLabel: string = "";
      if (label === undefined) {
        newLabel = currentEditText.trim();
      } else {
        newLabel = label;
      }

      if (newLabel.length == 0 || newLabel == BOOKMARK_LISTNAME_FAVORITE) {
        return;
      }

      try {
        const ret: IBookmarkUpdateListResponse = await updateBookmarkListAPI(
          bookmarkList.id,
          newLabel
        );

        if (ret.success) {
          dispatch(updateBookmarkList(ret.updated_item));
          setIsEditMode(false);
        }
      } catch (error) {}
    },
    [dispatch, currentEditText, bookmarkList, setIsEditMode]
  );

  const onChangeListText = async (e: any) => {
    setCurrentEditText(e.target.value);
  };

  const handleClickConfirmRenameModal = useCallback(
    async (value: boolean, newLabel?: string) => {
      setOpenRenameModal(false);
      if (value && newLabel !== undefined) {
        handleClickConfirmEdit(newLabel);
      }
    },
    [setOpenRenameModal, handleClickConfirmEdit]
  );

  const link = bookmarkListDetailPagePath(bookmarkList.id);

  const handleClickTitle = useCallback(async () => {
    if (isEditMode) {
      handleClickCancelEdit();
    } else {
      router.push(`${window.location.origin}${link}`);
    }
  }, [link, router, isEditMode, handleClickCancelEdit]);

  return (
    <div
      className={classNames(
        "flex w-full items-center bg-white rounded-lg pl-5 pr-2 py-4 mt-4 shadow-[0_8px_24px_rgba(129,135,189,0.15)] cursor-pointer",
        isFavorite && paperNum == 0 && searchNum == 0 ? "opacity-50" : ""
      )}
      onClick={handleClickTitle}
    >
      <div className="inline-flex items-center justify-center min-w-[40px] w-[40px] h-[40px] rounded-[5px] mr-4 bg-[#EEF0F1]">
        {isFavorite ? (
          <img
            src={"/icons/bookmark-black.svg"}
            className="w-[22px] h-[22px]"
            alt="bookmark icon"
          />
        ) : (
          <img
            src={"/icons/file.svg"}
            className="w-[22px] h-[22px]"
            alt="file icon"
          />
        )}
      </div>

      <div className="flex-1 flex flex-wrap items-center overflow-hidden">
        <span
          className={classNames(
            "block text-black text-left leading-none",
            isMobile ? "text-sm w-full" : "text-lg flex-1 w-auto"
          )}
        >
          {isMobile ? (
            <div className="text-sm text-ellipsis whitespace-nowrap overflow-hidden max-w-full">
              {bookmarkList.text_label}
            </div>
          ) : (
            <div
              className={classNames(
                "py-2 flex",
                isEditMode ? "bg-[#F1F4F6] px-4 rounded-lg" : ""
              )}
            >
              <input
                ref={inputRef}
                type="text"
                className={classNames(
                  "bg-transparent flex-1 outline-none text-ellipsis text-lg w-full",
                  !isEditMode ? "cursor-pointer" : ""
                )}
                value={isEditMode ? currentEditText : bookmarkList.text_label}
                maxLength={BOOKMARK_LISTNAME_MAX_LENGTH}
                readOnly={!isEditMode}
                onChange={onChangeListText}
                onClick={(e) => {
                  if (isEditMode) {
                    e.stopPropagation();
                  }
                }}
                onKeyUp={(e) => {
                  if (isEditMode && e.keyCode == 13) {
                    handleClickConfirmEdit(undefined);
                  }
                }}
              />

              {isEditMode && (
                <div className="flex items-center">
                  <img
                    src={"/icons/x-gray.svg"}
                    className="w-[20px] h-[20px] cursor-pointer"
                    alt="x icon"
                    onClick={(e: any) => {
                      e.preventDefault();
                      handleClickCancelEdit();
                    }}
                  />

                  <img
                    src={"/icons/check2-green.svg"}
                    className="w-[20px] h-[20px] cursor-pointer ml-3"
                    alt="check2 icon"
                    onClick={(e: any) => {
                      e.preventDefault();
                      handleClickConfirmEdit(undefined);
                    }}
                  />
                </div>
              )}
            </div>
          )}
        </span>

        <div
          className={classNames(
            "text-[#688092] text-left",
            isMobile ? "text-xs w-full mt-1" : "text-sm w-auto mt-0 ml-7"
          )}
        >
          {paperNum > 0 || searchNum > 0 ? (
            <div className="inline-flex flex-wrap items-center space-x-3">
              {paperNum > 0 && (
                <span>
                  {paperNum} paper{paperNum > 1 ? "s" : ""}
                </span>
              )}

              {paperNum > 0 && searchNum > 0 && <VerticalDivider />}

              {searchNum > 0 && (
                <span>
                  {searchNum} search{searchNum > 1 ? "es" : ""}
                </span>
              )}
            </div>
          ) : (
            <span>0 bookmarks</span>
          )}
        </div>
      </div>

      <div className="inline-flex pl-1">
        {!isFavorite && (
          <BookmarkListItemActionButton
            onClickEditList={handleClickEditList}
            onClickDeleteList={onClickDeleteList}
          />
        )}
      </div>

      <RenameModal
        open={openRenameModal}
        initialLabel={bookmarkList.text_label}
        onClose={(value: boolean, newLabel?: string) =>
          handleClickConfirmRenameModal(value, newLabel)
        }
      />
    </div>
  );
};

export default BookmarkListItem;
