import classNames from "classnames";
import VerticalDivider from "components/VerticalDivider";
import { BookmarkType, IBookmarkItem, ISearchBookmark } from "helpers/bookmark";
import { getSearchTextFromResultUrl } from "helpers/pageUrl";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import Link from "next/link";
import React, { ReactNode, useState } from "react";

type Props = {
  children?: ReactNode;
  bookmarkItem: IBookmarkItem;
  onClickRemoveBookmark?: () => void;
  onClickShare?: (url: string) => void;
};

/**
 * @component BookmarkSearchItem
 * @description designed for bookmark item
 * @example
 * return (
 *   <BookmarkSearchItem>Learn more</BookmarkSearchItem>
 * )
 */
const BookmarkSearchItem = ({
  children,
  bookmarkItem,
  onClickRemoveBookmark,
  onClickShare,
}: Props) => {
  const dispatch = useAppDispatch();
  const isMobile = useAppSelector((state) => state.setting.isMobile);
  const [isEditMode, setIsEditMode] = useState(false);
  const [currentEditText, setCurrentEditText] = useState<string>("");
  const [openRenameModal, setOpenRenameModal] = useState(false);
  let bookmarkSearchData: ISearchBookmark =
    bookmarkItem.bookmark_data as ISearchBookmark;

  const searchText = getSearchTextFromResultUrl(bookmarkSearchData.search_url);

  const link = "";

  return (
    <>
      {bookmarkItem.bookmark_type == BookmarkType.SEARCH && (
        <Link href={bookmarkSearchData.search_url} legacyBehavior>
          <a className="">
            <div
              className={classNames(
                "bg-white relative rounded-r-2xl bg-[#009FF5] flex shadow-[0_8px_24px_rgba(129,135,189,0.15)]",
                isMobile
                  ? "mb-8 rounded-l-lg pl-[6px]"
                  : "mb-4 rounded-l-xl pl-[10px]"
              )}
            >
              <div
                className={classNames(
                  "inline-flex w-full h-full bg-white min-h-[80px] items-center flex-1",
                  isMobile ? "rounded-r-lg" : ""
                )}
              >
                <img
                  className={classNames(
                    isMobile
                      ? "w-[24px] h-[24px] ml-1"
                      : "w-[40px] h-[40px] ml-4"
                  )}
                  alt="Info"
                  src="/icons/input-search-icon.svg"
                />

                <div
                  className={classNames(
                    "ml-2 text-left text-black mt-4 mb-4",
                    isMobile ? "text-[16px]" : "text-[20px]"
                  )}
                >
                  <span>{searchText}</span>
                </div>
              </div>

              <div
                className={classNames(
                  "bg-white flex items-center pr-7 rounded-r-xl",
                  isMobile ? "hidden" : ""
                )}
              >
                <button
                  className="flex items-center h-full mr-3"
                  onClick={(e) => {
                    e.preventDefault();
                    if (onClickRemoveBookmark) {
                      onClickRemoveBookmark();
                    }
                  }}
                >
                  <img
                    src={"/icons/bookmark-blue.svg"}
                    className="w-[20px] h-[20px] mr-2"
                    alt="bookmark icon"
                  />
                  <span>Saved</span>
                </button>

                <VerticalDivider />

                <button
                  className="flex items-center ml-3"
                  onClick={(e) => {
                    e.preventDefault();
                    if (onClickShare) {
                      onClickShare(bookmarkSearchData.search_url);
                    }
                  }}
                >
                  <img
                    src={"/icons/share.svg"}
                    className="w-[20px] h-[20px] mr-2"
                    alt="bookmark icon"
                  />
                  <span>Share</span>
                </button>
              </div>

              <div
                className={classNames(
                  "absolute items-center space-x-3 right-4 z-10 bottom-0 -mb-4",
                  isMobile ? "flex" : "hidden"
                )}
              >
                <button
                  className="flex items-center justify-center h-full bg-white w-[40px] h-[40px] rounded-full shadow-[0_4px_20px_rgba(189,201,219,0.26)]"
                  onClick={(e) => {
                    e.preventDefault();
                    if (onClickRemoveBookmark) {
                      onClickRemoveBookmark();
                    }
                  }}
                >
                  <img
                    src={"/icons/bookmark-blue.svg"}
                    className="w-[20px] h-[20px]"
                    alt="bookmark icon"
                  />
                </button>

                <button
                  className="flex items-center justify-center  bg-white w-[40px] h-[40px] rounded-full shadow-[0_4px_20px_rgba(189,201,219,0.26)]"
                  onClick={(e) => {
                    e.preventDefault();
                    if (onClickShare) {
                      onClickShare(bookmarkSearchData.search_url);
                    }
                  }}
                >
                  <img
                    src={"/icons/share.svg"}
                    className="w-[20px] h-[20px]"
                    alt="bookmark icon"
                  />
                </button>
              </div>
            </div>
          </a>
        </Link>
      )}
    </>
  );
};

export default BookmarkSearchItem;
