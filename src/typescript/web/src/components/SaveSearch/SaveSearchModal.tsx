import { useAuth } from "@clerk/nextjs";
import classNames from "classnames";
import Icon, { IconLoader } from "components/Icon";
import Modal from "components/Modal";
import Tooltip from "components/Tooltip";
import CreateBookmarkItemTooltip from "components/Tooltip/CreateBookmarkItemTooltip/CreateBookmarkItemTooltip";
import CreateBookmarkListTooltip from "components/Tooltip/CreateBookmarkListTooltip/CreateBookmarkListTooltip";
import {
  BOOKMARK_LISTNAME_FAVORITE,
  BOOKMARK_LISTNAME_MAX_LENGTH,
  BOOKMARK_MAX_ITEM_NUM,
} from "constants/config";
import path from "constants/path";
import {
  createBookmarkItemsAPI,
  createBookmarkListAPI,
  deleteBookmarkItemAPI,
} from "helpers/api";
import {
  findBookmarkItem,
  getBookmarkItemsCount,
  IBookmarkCreateItemData,
  IBookmarkCreateItemsResponse,
  IBookmarkCreateListResponse,
  IBookmarkItem,
  IBookmarkListItem,
} from "helpers/bookmark";
import { isResultsPageUrl } from "helpers/pageUrl";
import useLabels from "hooks/useLabels";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import { useRouter } from "next/router";
import React, { useCallback, useEffect, useState } from "react";
import {
  addBookmarkItem,
  addBookmarkList,
  BookmarkItemsType,
  checkList,
  removeBookmarkItem,
  uncheckList,
} from "store/slices/bookmark";

type SaveSearchModalProps = {
  open?: boolean;
  onClose: (value: boolean) => void;
};

/**
 * @component SaveSearchModal
 * @description Component for save search modal
 * @example
 * return (
 *   <SaveSearchModal
 *    open={true}
 *    onClose={fn}
 *   />
 * )
 */
function SaveSearchModal({ open, onClose }: SaveSearchModalProps) {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const { isSignedIn, isLoaded } = useAuth();
  const [showCreateNewList, setShowCreateNewList] = useState(false);
  const [modalLabels] = useLabels("save-search-modal");
  const [createNewListLabels] = useLabels("create-new-list-modal");
  const bookmarkSaveSearchState = useAppSelector(
    (state) => state.bookmark.bookmarkSaveSearchState
  );
  const subscription = useAppSelector(
    (state) => state.subscription.subscription
  );
  const isLoadedSubscription = useAppSelector(
    (state) => state.subscription.isLoadedSubscription
  );
  const bookmarkLists = useAppSelector((state) => state.bookmark.bookmarkLists);
  const isLimitedBookmarkList = useAppSelector(
    (state) => state.bookmark.isLimitedBookmarkList
  );
  const bookmarkItems: BookmarkItemsType = useAppSelector(
    (state) => state.bookmark.bookmarkItems
  );
  const isBookmarkItemsLoaded = useAppSelector(
    (state) => state.bookmark.isBookmarkItemsLoaded
  );
  const isBookmarkListLoaded = useAppSelector(
    (state) => state.bookmark.isBookmarkListLoaded
  );
  const selectedListIds = useAppSelector(
    (state) => state.bookmark.selectedListIds
  );

  const [newListInputValue, setNewListInputValue] = useState<string>("");
  const [isCreatingList, setIsCreatingList] = useState<Boolean>(false);
  const [isCreatingItems, setIsCreatingItems] = useState<Boolean>(false);
  const [initialSelectedListNum, setInitialSelectedListNum] = useState<
    number | undefined
  >(undefined);
  const [tooltipInstance, setTooltipInstance] = useState<any>(null);
  const isPremiumPopupOpen = useAppSelector(
    (state) => state.subscription.openUpgradeToPremiumPopup
  );
  const [isFutureBookmarkItemLimited, setIsFutureBookmarkItemLimited] =
    useState<Boolean>(true);
  const handleClickCancelCreateNewList = () => {
    setShowCreateNewList(false);
  };

  const handleClickCancel = useCallback(async () => {
    onClose(true);
    setShowCreateNewList(false);
    setInitialSelectedListNum(undefined);
  }, [setShowCreateNewList, onClose]);

  const handleClickSave = useCallback(async () => {
    if (isBookmarkItemsLoaded !== true || isBookmarkListLoaded !== true) {
      return;
    }

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

    if (!isCreatingItems) {
      setIsCreatingItems(true);

      let toBeDeletedBookmarkItems: IBookmarkItem[] = [];
      let toBeDeletedBookmarkItemsIdList: number[] = [];
      for (let i = 0; i < bookmarkLists.length; i++) {
        const bookmarkList: IBookmarkListItem = bookmarkLists[i];
        if (selectedListIds.includes(bookmarkList.id) == false) {
          const bookmarkItem = findBookmarkItem(
            bookmarkSaveSearchState,
            bookmarkList.id,
            bookmarkItems
          );
          if (bookmarkItem != null) {
            toBeDeletedBookmarkItems.push(bookmarkItem);
            toBeDeletedBookmarkItemsIdList.push(bookmarkItem.id);
          }
        }
      }

      if (toBeDeletedBookmarkItemsIdList.length > 0) {
        const deletionPromises = toBeDeletedBookmarkItemsIdList.map((id) =>
          deleteBookmarkItemAPI(id)
        );

        const results = await Promise.allSettled(deletionPromises);

        toBeDeletedBookmarkItems.forEach((item) => {
          if (
            results.find(
              (result) =>
                result.status === "fulfilled" &&
                result.value.success &&
                Number(result.value.id) === item.id
            )
          )
            dispatch(removeBookmarkItem(item));
        });
      }

      let toCreateBookmarkItems: IBookmarkCreateItemData[] = [];
      for (let i = 0; i < selectedListIds.length; i++) {
        const item: IBookmarkCreateItemData = {
          list_id: selectedListIds[i],
          search_url: bookmarkSaveSearchState.searchUrl,
          paper_id: bookmarkSaveSearchState.paperId,
        };
        toCreateBookmarkItems.push(item);
      }

      try {
        const ret: IBookmarkCreateItemsResponse = await createBookmarkItemsAPI(
          toCreateBookmarkItems
        );

        if (ret.success) {
          for (let i = 0; i < ret.created_items.length; i++) {
            dispatch(addBookmarkItem(ret.created_items[i]));
          }
        }
      } catch (error) {}

      setIsCreatingItems(false);
      handleClickCancel();
    }
  }, [
    dispatch,
    router,
    isSignedIn,
    isLoaded,
    setIsCreatingItems,
    selectedListIds,
    bookmarkSaveSearchState,
    bookmarkLists,
    bookmarkItems,
    isBookmarkItemsLoaded,
    isBookmarkListLoaded,
    handleClickCancel,
    isCreatingItems,
  ]);

  const onChangeNewListLabel = async (e: any) => {
    setNewListInputValue(e.target.value);
  };

  const handleClickShowCreateNewList = useCallback(async () => {
    if (isResultsPageUrl(router.route)) {
      setNewListInputValue(router.query.q as string);
    }
    setShowCreateNewList(true);
  }, [router]);

  const handleClickList = useCallback(
    async (id: string) => {
      if (initialSelectedListNum === undefined) {
        setInitialSelectedListNum(selectedListIds.length);
      }
      if (selectedListIds.includes(id)) {
        dispatch(uncheckList(id));
      } else {
        dispatch(checkList(id));
      }
    },
    [dispatch, selectedListIds, initialSelectedListNum]
  );

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

          const futureBookmarkItemCount =
            getBookmarkItemsCount(bookmarkItems) +
            (selectedListIds.length -
              (initialSelectedListNum === undefined
                ? selectedListIds.length
                : initialSelectedListNum));
          if (
            subscription.org != null ||
            subscription.user != null ||
            futureBookmarkItemCount < BOOKMARK_MAX_ITEM_NUM
          ) {
            handleClickList(ret.created_item.id);
          }
        }
      } catch (error) {}
      setIsCreatingList(false);
      setShowCreateNewList(false);
    }
  }, [
    dispatch,
    router,
    isSignedIn,
    isLoaded,
    isLimitedBookmarkList,
    newListInputValue,
    isCreatingList,
    bookmarkItems,
    selectedListIds,
    initialSelectedListNum,
    subscription,
    handleClickList,
  ]);

  useEffect(() => {
    if (isLoadedSubscription && isBookmarkItemsLoaded) {
      const futureBookmarkItemCount =
        getBookmarkItemsCount(bookmarkItems) +
        (selectedListIds.length -
          (initialSelectedListNum === undefined
            ? selectedListIds.length
            : initialSelectedListNum));
      if (
        subscription.org != null ||
        subscription.user != null ||
        futureBookmarkItemCount < BOOKMARK_MAX_ITEM_NUM
      ) {
        setIsFutureBookmarkItemLimited(false);
      } else {
        setIsFutureBookmarkItemLimited(true);
      }
    }
  }, [
    selectedListIds,
    initialSelectedListNum,
    subscription,
    isLoadedSubscription,
    isBookmarkListLoaded,
    isBookmarkItemsLoaded,
    bookmarkItems,
    bookmarkLists,
  ]);

  useEffect(() => {
    if (isPremiumPopupOpen) {
      if (tooltipInstance != null) {
        tooltipInstance.hide();
      }
    }
  }, [isPremiumPopupOpen, tooltipInstance]);

  return (
    <>
      <Modal
        open={open}
        onClose={handleClickCancel}
        size="md"
        padding={false}
        mobileFit={true}
        additionalClass={"mt-[60px] max-w-[565px]"}
      >
        <div
          className="py-12 px-[20px] md:p-12 bg-[url('/images/bg-card.webp')] bg-no-repeat bg-cover rounded-lg leading-none"
          data-testid="save-search-modal"
        >
          {!showCreateNewList && (
            <>
              <div>
                <h3 className="max-w-sm mx-auto text-2xl font-bold text-center text-black">
                  {modalLabels["title"]}
                </h3>
              </div>

              <div className="mt-9">
                {bookmarkLists.length > 0 && (
                  <>
                    <Tooltip
                      interactive
                      maxWidth={340}
                      onShown={(instance: any) => {
                        setTooltipInstance(instance);
                      }}
                      onHidden={(instance: any) => {
                        setTooltipInstance(instance);
                      }}
                      tooltipContent={<CreateBookmarkListTooltip />}
                      className="rounded-xl"
                      widthFull={true}
                      disabled={isLimitedBookmarkList !== true}
                    >
                      <button
                        className="flex items-center w-full p-3 bg-white rounded-lg"
                        onClick={(e) => {
                          if (isLimitedBookmarkList === false) {
                            handleClickShowCreateNewList();
                          }
                        }}
                      >
                        <div className="inline-flex items-center justify-center w-[40px] h-[40px] rounded-[5px] mr-4">
                          <Icon
                            size={24}
                            className="text-[#0A6DC2]"
                            name="plus"
                          />
                        </div>
                        <span className="text-base text-[#303A40]">
                          {modalLabels["create-new-list"]}
                        </span>
                      </button>
                    </Tooltip>
                  </>
                )}

                <div className="max-h-[250px] overflow-y-auto">
                  {bookmarkLists.map((bookmarkList: IBookmarkListItem) => (
                    <Tooltip
                      key={bookmarkList.id}
                      interactive
                      maxWidth={340}
                      onShown={(instance: any) => {
                        setTooltipInstance(instance);
                      }}
                      onHidden={(instance: any) => {
                        setTooltipInstance(instance);
                      }}
                      tooltipContent={<CreateBookmarkItemTooltip />}
                      className="rounded-xl"
                      widthFull={true}
                      disabled={
                        selectedListIds.includes(bookmarkList.id) ||
                        !isFutureBookmarkItemLimited
                      }
                    >
                      <button
                        key={bookmarkList.id}
                        className="flex items-center w-full p-3 mt-3 bg-white rounded-lg"
                        onClick={(e) => {
                          if (
                            selectedListIds.includes(bookmarkList.id) ||
                            !isFutureBookmarkItemLimited
                          ) {
                            handleClickList(bookmarkList.id);
                          }
                        }}
                      >
                        <div className="inline-flex items-center justify-center min-w-[40px] w-[40px] h-[40px] rounded-[5px] mr-4 bg-[#EEF0F1]">
                          {bookmarkList.text_label ==
                          BOOKMARK_LISTNAME_FAVORITE ? (
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
                        <div className="flex-1 mr-3 overflow-hidden">
                          <span className="block text-base text-[#303A40] text-left leading-none text-ellipsis whitespace-nowrap overflow-hidden max-w-full">
                            {bookmarkList.text_label}
                          </span>
                          <span className="block text-xs text-[#688092] text-left">
                            {bookmarkItems &&
                            bookmarkItems.hasOwnProperty(bookmarkList.id)
                              ? bookmarkItems[bookmarkList.id].length
                              : 0}{" "}
                            {modalLabels["items"]}
                          </span>
                        </div>

                        {selectedListIds.includes(bookmarkList.id) ? (
                          <img
                            src={"/icons/checked.svg"}
                            className="w-[20px] h-[20px] mr-3"
                            alt="checked icon"
                          />
                        ) : (
                          <img
                            src={"/icons/unchecked.svg"}
                            className="w-[20px] h-[20px] mr-3"
                            alt="unchecked icon"
                          />
                        )}
                      </button>
                    </Tooltip>
                  ))}
                </div>
              </div>

              <div className="mt-6">
                <button
                  onClick={handleClickSave}
                  data-testid="button-save"
                  className={classNames(
                    "flex w-full justify-center bg-[#0A6DC2] border border-[#0A6DC2] text-white py-2.5 rounded-full items-center cursor-pointer mt-4 disabled:opacity-60 disabled:cursor-not-allowed"
                  )}
                  disabled={Boolean(isCreatingItems)}
                >
                  {isCreatingItems ? (
                    <div className="w-[36px] h-[24px] -mr-3 -mt-2 text-white">
                      <IconLoader color="#FFFFFF" />
                    </div>
                  ) : (
                    <span>{modalLabels["done"]}</span>
                  )}
                </button>

                <button
                  onClick={handleClickCancel}
                  data-testid="button-cancel"
                  className="flex w-full justify-center bg-white border border-[#D6D2D6] text-white py-2.5 rounded-full items-center cursor-pointer mt-4"
                >
                  <span className="text-[#000000]">
                    {modalLabels["cancel"]}
                  </span>
                </button>
              </div>
            </>
          )}

          {showCreateNewList && (
            <>
              <div>
                <h3 className="max-w-sm mx-auto text-2xl font-bold text-center text-black">
                  {createNewListLabels["title"]}
                </h3>
              </div>

              <div className="mt-9">
                <span className="block text-base text-[#303A40] ml-1">
                  {createNewListLabels["list-name"]}
                </span>

                <div className="p-1 mt-1 rounded-lg bg-white/50">
                  <input
                    type="text"
                    className="w-full border border-[#2AA3EF]/50 focus:border-[#2AA3EF]/50 hover:border-[#2AA3EF]/50 outline-none px-4 py-3 bg-white rounded-lg text-black"
                    maxLength={60}
                    onChange={onChangeNewListLabel}
                    value={newListInputValue}
                    autoFocus
                    onKeyUp={(e) => {
                      if (!isCreatingList && e.keyCode == 13) {
                        handleClickCreateNewList();
                      }
                    }}
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
                  onClick={handleClickCancelCreateNewList}
                  data-testid="button-cancel"
                  className="flex w-full justify-center bg-white border border-[#D6D2D6] text-white py-2.5 rounded-full items-center cursor-pointer mt-4"
                >
                  <span className="text-[#000000]">
                    {createNewListLabels["cancel"]}
                  </span>
                </button>
              </div>
            </>
          )}
        </div>
      </Modal>
    </>
  );
}

export default SaveSearchModal;
