import Button from "components/Button";
import {
  BOOKMARK_MAX_CUSTOM_LIST_NUM,
  BOOKMARK_MAX_ITEM_NUM,
} from "constants/config";
import { getBookmarkItemsCount } from "helpers/bookmark";
import useLabels from "hooks/useLabels";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import React, { useCallback } from "react";
import { setOpenUpgradeToPremiumPopup } from "store/slices/subscription";

interface BookmarkListsUpsellProps {
  isPremium: boolean;
}

function BookmarkListsUpsell({ isPremium }: BookmarkListsUpsellProps) {
  const dispatch = useAppDispatch();
  const [pageLabels] = useLabels("screens.bookmark-lists");

  const bookmarkLists = useAppSelector((state) => state.bookmark.bookmarkLists);
  const bookmarkItems = useAppSelector((state) => state.bookmark.bookmarkItems);
  const bookmarkItemNum = getBookmarkItemsCount(bookmarkItems);
  const bookmarkListLeft =
    BOOKMARK_MAX_CUSTOM_LIST_NUM - bookmarkLists.length + 1;
  const bookmarkItemsLeft = BOOKMARK_MAX_ITEM_NUM - bookmarkItemNum;
  const handleClickUpgradePremium = useCallback(async () => {
    dispatch(setOpenUpgradeToPremiumPopup(true));
  }, [dispatch]);

  if (isPremium) {
    return <></>;
  }

  return (
    <div className="mt-6 flex flex-wrap items-center justify-between">
      <div className="flex items-center ">
        <span
          data-testid="title1"
          className="text-black text-base md:text-lg font-bold text-left leading-none"
        >
          {pageLabels["want-unlimited"]}
        </span>

        <Button
          data-testid="upsell-upgrade-button"
          type="button"
          className="text-[#0A6DC2] justify-start flex items-center text-base font-bold gap-x-[8px] ml-6"
          onClick={handleClickUpgradePremium}
        >
          <img
            src={"/icons/premium.svg"}
            className="w-[20px] h-[20px]"
            alt="premium icon"
          />
          <span data-testid="title2" className="text-left leading-none">
            {pageLabels["upgrade-to-premium"]}
          </span>
        </Button>
      </div>

      <div className="w-full md:w-auto mt-2 md:mt-0 flex items-center">
        <span className="text-sm text-[#688092]">
          <span data-testid="lists-left-text">
            {pageLabels["custom-lists-left"]}
          </span>
          <span className="text-base text-[#222F2B] ml-2">
            {bookmarkListLeft >= 0 ? bookmarkListLeft : 0}
          </span>
        </span>

        <span className="w-[1px] h-[17px] ml-3 mr-3 inline-block bg-[#DEE0E3]"></span>

        <span className="text-sm text-[#688092]">
          <span data-testid="items-left-text">
            {pageLabels["bookmarks-left"]}
          </span>
          <span className="text-base text-[#222F2B] ml-2">
            {bookmarkItemsLeft >= 0 ? bookmarkItemsLeft : 0}
          </span>
        </span>
      </div>
    </div>
  );
}

export default BookmarkListsUpsell;
