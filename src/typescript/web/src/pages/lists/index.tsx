import BookmarkListItem from "components/Bookmark/BookmarkListItem";
import BookmarkListsUpsell from "components/Bookmark/BookmarkListsUpsell";
import ConfirmDeleteListModal from "components/Bookmark/ConfirmDeleteListModal";
import Head from "components/Head";
import Icon from "components/Icon";
import CreateNewListModal from "components/SaveSearch/CreateNewListModal";
import Tooltip from "components/Tooltip";
import CreateBookmarkListTooltip from "components/Tooltip/CreateBookmarkListTooltip/CreateBookmarkListTooltip";
import { deleteBookmarkListAPI } from "helpers/api";
import {
  IBookmarkDeleteListResponse,
  IBookmarkItem,
  IBookmarkListItem,
} from "helpers/bookmark";
import { isSubscriptionPremium } from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import type { NextPage } from "next";
import { useCallback, useState } from "react";
import { removeBookmarkItem, removeBookmarkList } from "store/slices/bookmark";

/**
 * @page Bookmark Lists Page
 * @description page for managing bookmark lists
 */
const BookmarkListsPage: NextPage<void> = () => {
  const [pageLabels] = useLabels("screens.bookmark-lists");
  const dispatch = useAppDispatch();
  const subscription = useAppSelector(
    (state) => state.subscription.subscription
  );
  const bookmarkLists = useAppSelector((state) => state.bookmark.bookmarkLists);
  const bookmarkItems = useAppSelector((state) => state.bookmark.bookmarkItems);
  const isLimitedBookmarkList = useAppSelector(
    (state) => state.bookmark.isLimitedBookmarkList
  );
  const isBookmarkListLoaded = useAppSelector(
    (state) => state.bookmark.isBookmarkListLoaded
  );
  const isBookmarkItemsLoaded = useAppSelector(
    (state) => state.bookmark.isBookmarkItemsLoaded
  );
  const isPremium = isSubscriptionPremium(subscription);
  const [currentListId, setCurrentListId] = useState<string | undefined>(
    undefined
  );
  const [openCreateNewListModal, setOpenCreateNewListModal] = useState(false);
  const [openConfirmDeleteListModal, setOpenConfirmDeleteListModal] =
    useState(false);

  const handleClickCreateNewList = async () => {
    setOpenCreateNewListModal(true);
  };

  const handleClickCancelCreateNewList = async () => {
    setOpenCreateNewListModal(false);
  };

  const handleClickDeleteList = async (listId: string) => {
    setCurrentListId(listId);
    setOpenConfirmDeleteListModal(true);
  };

  const handleClickCloseConfirmDeleteList = useCallback(
    async (value: boolean) => {
      setOpenConfirmDeleteListModal(false);

      if (
        value &&
        currentListId != undefined &&
        isBookmarkListLoaded &&
        isBookmarkItemsLoaded
      ) {
        const ret: IBookmarkDeleteListResponse = await deleteBookmarkListAPI(
          currentListId
        );
        if (ret.success) {
          if (bookmarkItems && bookmarkItems.hasOwnProperty(currentListId)) {
            const toDeleteItems: IBookmarkItem[] = bookmarkItems[currentListId];
            for (let i = 0; i < toDeleteItems.length; i++) {
              const item: IBookmarkItem = toDeleteItems[i];
              dispatch(removeBookmarkItem(item));
            }
          }
          dispatch(removeBookmarkList(currentListId));
        }
        setCurrentListId(undefined);
      }
    },
    [
      dispatch,
      setOpenConfirmDeleteListModal,
      setCurrentListId,
      currentListId,
      bookmarkItems,
      isBookmarkListLoaded,
      isBookmarkItemsLoaded,
    ]
  );

  return (
    <>
      <Head
        title={pageLabels["title"]}
        description={pageLabels["description"]}
      />
      <div
        data-testid="bookmark-lists"
        className="container max-w-6xl m-auto mt-10 mb-20 text-center md:mt-20"
      >
        <div className="flex justify-between">
          <h1 className="text-2xl font-bold text-black md:text-4xl">
            {pageLabels["page-title"]}
          </h1>

          <button
            className="inline-flex items-center bg-white rounded-full border border-[#DEE0E3] px-5 relative"
            onClick={handleClickCreateNewList}
            disabled={!(isLimitedBookmarkList === false)}
          >
            <Icon size={20} className="text-[#889CAA] mr-2" name="plus" />
            <span className="text-base text-black">
              {pageLabels["create-new-list"]}
            </span>

            {isLimitedBookmarkList === true && (
              <Tooltip
                interactive
                maxWidth={340}
                onShown={(instance: any) => {}}
                onHidden={(instance: any) => {}}
                tooltipContent={<CreateBookmarkListTooltip />}
                className="ml-5 rounded-xl mt-7 premium-bookmark-popup"
              >
                <span className="absolute top-0 left-0 w-full h-full"></span>
              </Tooltip>
            )}
          </button>
        </div>

        <BookmarkListsUpsell isPremium={isPremium} />

        <div className="mt-3 md:mt-5">
          {bookmarkLists.map((bookmarkList: IBookmarkListItem) => (
            <BookmarkListItem
              key={bookmarkList.id}
              bookmarkList={bookmarkList}
              onClickDeleteList={() => {
                handleClickDeleteList(bookmarkList.id);
              }}
            />
          ))}
        </div>
      </div>

      <CreateNewListModal
        open={openCreateNewListModal}
        onClose={handleClickCancelCreateNewList}
      />

      <ConfirmDeleteListModal
        open={openConfirmDeleteListModal}
        onClose={handleClickCloseConfirmDeleteList}
      />
    </>
  );
};

export default BookmarkListsPage;
