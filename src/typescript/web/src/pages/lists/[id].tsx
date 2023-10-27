import { useAuth } from "@clerk/nextjs";
import { withServerSideAuth } from "@clerk/nextjs/ssr";
import classNames from "classnames";
import BookmarkEmpty from "components/Bookmark/BookmarkEmpty";
import BookmarkSearchItem from "components/Bookmark/BookmarkSearchItem";
import ConfirmDeleteListModal from "components/Bookmark/ConfirmDeleteListModal";
import RenameModal from "components/Bookmark/RenameModal";
import { CardSearchResults } from "components/Card";
import CiteModal from "components/CiteModal/CiteModal";
import Head from "components/Head";
import Icon from "components/Icon";
import LoadingSearchResult from "components/LoadingSearchResult";
import ShareModal from "components/ShareModal/ShareModal";
import {
  BOOKMARK_LISTNAME_FAVORITE,
  BOOKMARK_LISTNAME_MAX_LENGTH,
} from "constants/config";
import path from "constants/path";
import { FeatureFlag } from "enums/feature-flag";
import {
  deleteBookmarkItemAPI,
  deleteBookmarkListAPI,
  getPapersList,
  GetPapersListOptions,
  ISearchItem,
  PapersListResponse,
  updateBookmarkListAPI,
} from "helpers/api";
import {
  BookmarkType,
  findBookmarkItem,
  getPaperSearchNum,
  hasBookmarkListItemsDifference,
  IBookmarkDeleteItemResponse,
  IBookmarkDeleteListResponse,
  IBookmarkItem,
  IBookmarkUpdateListResponse,
  IPaperBookmark,
} from "helpers/bookmark";
import { getCite } from "helpers/cite";
import {
  getSearchTextFromResultUrl,
  paperDetailPagePath,
} from "helpers/pageUrl";
import parseSubText from "helpers/parseSubText";
import useAnalytics from "hooks/useAnalytics";
import useCite from "hooks/useCite";
import useIsFeatureEnabled from "hooks/useIsFeatureEnabled";
import useLabels from "hooks/useLabels";
import useShare from "hooks/useShare";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import type { NextPage } from "next";
import Link from "next/link";
import { useRouter } from "next/router";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  BookmarkSaveSearchState,
  removeBookmarkItem,
  removeBookmarkList,
  updateBookmarkList,
} from "store/slices/bookmark";

type BookmarkListDetailPageProps = {
  id: string;
};

enum PageTab {
  PaperTab = "paper tab",
  SearchTab = "search tab",
}

/**
 * @page Bookmark List Detail Page
 * @description page for bookmark list detail page
 */
const BookmarkListDetailPage: NextPage<BookmarkListDetailPageProps> = ({
  id,
}: BookmarkListDetailPageProps) => {
  const { clickShareEvent, executeShareEvent, setAnalyticSearchItem } =
    useAnalytics();
  const listNameRef = useRef<any>(null);
  const router = useRouter();
  const { isSignedIn, isLoaded } = useAuth();
  const isMobile = useAppSelector((state) => state.setting.isMobile);
  const [pageLabels] = useLabels("screens.bookmark-list-detail");
  const [searchPageLabels] = useLabels("screens.search");
  const [detailLabels] = useLabels("screens.details");

  const dispatch = useAppDispatch();
  const bookmarkLists = useAppSelector((state) => state.bookmark.bookmarkLists);
  const bookmarkItems = useAppSelector((state) => state.bookmark.bookmarkItems);
  const isBookmarkListLoaded = useAppSelector(
    (state) => state.bookmark.isBookmarkListLoaded
  );
  const isBookmarkItemsLoaded = useAppSelector(
    (state) => state.bookmark.isBookmarkItemsLoaded
  );
  const [bookmarkListTitle, setBookmarkListTitle] = useState("");
  const [isListExist, setIsListExist] = useState<boolean | undefined>(
    undefined
  );
  const [bookmarkListItems, setBookmarkListItems] = useState<IBookmarkItem[]>(
    []
  );
  const [selectedTab, setSelectedTab] = useState<PageTab>(PageTab.PaperTab);
  const [openConfirmDeleteListModal, setOpenConfirmDeleteListModal] =
    useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [currentEditText, setCurrentEditText] = useState<string>("");
  const [openRenameModal, setOpenRenameModal] = useState(false);
  const [paperDetailItems, setPaperDetailItems] = useState<ISearchItem[]>([]);
  const [isLoadingPaperDetailItems, setIsLoadingPaperDetailItems] =
    useState(true);
  const [previousBookmarkListItems, setPreviousBookmarkListItems] = useState<
    IBookmarkItem[]
  >([]);
  const features = {
    enablePaperSearch: useIsFeatureEnabled(FeatureFlag.PAPER_SEARCH),
  };

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push(
        `${path.SIGN_UP}#/?redirect_url=${encodeURIComponent(
          `${router?.asPath}`
        )}`
      );
      return;
    }

    if (isBookmarkListLoaded && isBookmarkItemsLoaded) {
      let listExist: boolean = false;
      for (let i = 0; i < bookmarkLists.length; i++) {
        if (bookmarkLists[i].id == id) {
          setBookmarkListTitle(bookmarkLists[i].text_label);
          listExist = true;
          break;
        }
      }
      setIsListExist(listExist);

      if (bookmarkItems && bookmarkItems.hasOwnProperty(id)) {
        setBookmarkListItems(bookmarkItems[id]);
      }
    }
  }, [
    id,
    isBookmarkListLoaded,
    isBookmarkItemsLoaded,
    bookmarkLists,
    bookmarkItems,
    setBookmarkListTitle,
    setBookmarkListItems,
    isSignedIn,
    isLoaded,
    router,
  ]);

  const handleClickDeleteList = useCallback(async () => {
    setOpenConfirmDeleteListModal(true);
  }, [setOpenConfirmDeleteListModal]);

  const handleClickEditList = useCallback(async () => {
    if (isMobile) {
      setCurrentEditText(bookmarkListTitle);
      setOpenRenameModal(true);
    } else {
      setCurrentEditText(bookmarkListTitle);
      setIsEditMode(true);
    }

    if (listNameRef != null && listNameRef.current != null) {
      listNameRef.current.focus();
    }
  }, [
    isMobile,
    bookmarkListTitle,
    setIsEditMode,
    setCurrentEditText,
    setOpenRenameModal,
    listNameRef,
  ]);

  const handleClickCloseConfirmDeleteList = useCallback(
    async (value: boolean) => {
      setOpenConfirmDeleteListModal(false);

      if (value && isBookmarkItemsLoaded) {
        const ret: IBookmarkDeleteListResponse = await deleteBookmarkListAPI(
          id
        );
        if (ret.success) {
          if (bookmarkItems && bookmarkItems.hasOwnProperty(id)) {
            const toDeleteItems: IBookmarkItem[] = bookmarkItems[id];
            for (let i = 0; i < toDeleteItems.length; i++) {
              const item: IBookmarkItem = toDeleteItems[i];
              dispatch(removeBookmarkItem(item));
            }
          }
          dispatch(removeBookmarkList(id));
        }
        await router.replace(path.LISTS);
      }
    },
    [
      router,
      dispatch,
      setOpenConfirmDeleteListModal,
      bookmarkItems,
      isBookmarkItemsLoaded,
      id,
    ]
  );

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
          id,
          newLabel
        );

        if (ret.success) {
          setBookmarkListTitle(newLabel);
          dispatch(updateBookmarkList(ret.updated_item));
          setIsEditMode(false);
        }
      } catch (error) {}
    },
    [dispatch, currentEditText, setIsEditMode, id]
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

  useEffect(() => {
    (async () => {
      if (
        hasBookmarkListItemsDifference(
          previousBookmarkListItems,
          bookmarkListItems
        )
      ) {
        setIsLoadingPaperDetailItems(true);
        setPreviousBookmarkListItems(bookmarkListItems);

        const paperBookmarks = bookmarkListItems.filter(
          (x) => x.bookmark_type == BookmarkType.PAPER
        );

        const paperIds: string[] = paperBookmarks.map(
          (x) => (x.bookmark_data as IPaperBookmark).paper_id
        );

        const resultItems: ISearchItem[] = [];
        if (paperIds.length > 0) {
          const options: GetPapersListOptions = {
            includeAbstract: false,
            includeJournal: false,
            enablePaperSearch: features.enablePaperSearch,
          };
          const resDict: PapersListResponse = await getPapersList(
            paperIds,
            options
          );

          for (const detailItemKey in resDict.paperDetailsListByPaperId) {
            const paperDetails =
              resDict.paperDetailsListByPaperId[detailItemKey];
            const searchItem: ISearchItem = {
              id: paperDetails.id,
              paper_id: paperDetails.id,
              text: paperDetails.abstract_takeaway,
              url_slug: paperDetails.url_slug || "",
              journal: paperDetails.journal.title,
              title: paperDetails.title,
              year: paperDetails.year,
              primary_author: paperDetails.authors[0],
              badges: paperDetails.badges,
              score: 0,
              volume: "",
              pages: "",
            };

            resultItems.push(searchItem);
          }
        }

        setPaperDetailItems(resultItems);
        setIsLoadingPaperDetailItems(false);
      } else {
        setIsLoadingPaperDetailItems(false);
      }
    })();
    return () => {};
  }, [
    bookmarkListItems,
    previousBookmarkListItems,
    setPreviousBookmarkListItems,
  ]);

  const { paperNum, searchNum } = getPaperSearchNum(id, bookmarkItems);

  const { handleShare, openShare, handleCloseShare, shareData, setShareData } =
    useShare();
  const { handleCite, openCite, handleCloseCite, citeData, setCiteData } =
    useCite();

  const handleClickShareItem = (item: ISearchItem, index: number) => {
    const link = paperDetailPagePath(item.url_slug, item.paper_id);
    setShareData({
      url: `${window.location.origin}${link}`,
      title: searchPageLabels["share-this-finding"],
      shareText: detailLabels["share-text"],
      text: item.text,
      subText: parseSubText(item),
      isDetail: true,
    });

    handleShare({
      title: `${item.title} - Consensus`,
      url: `${window.location.origin}${link}`,
    });

    // analytic
    setAnalyticSearchItem(item);
    clickShareEvent();
  };

  const handleClickShareSearchItem = (search_url: string) => {
    const queryText = getSearchTextFromResultUrl(search_url);
    setShareData({
      url: `${window.location.origin}${search_url}`,
      title: pageLabels["share-title"],
      shareText: pageLabels["share-text"],
      text: queryText,
      subText: "",
      isDetail: false,
    });

    handleShare({
      title: queryText,
      url: `${window.location.origin}${search_url}`,
    });
  };

  const handleClickCiteItem = (item: ISearchItem) => {
    const { mla, apa, chicago, bibtex, harvard } = getCite({
      authors: item?.authors,
      author: item.primary_author,
      journal: item.journal,
      title: item.title,
      year: item.year,
      doi: item.doi,
      volume: item.volume,
      pages: item.pages,
    });

    setCiteData({
      apa,
      mla,
      bibtex,
      chicago,
      harvard,
    });

    handleCite();
  };

  const handleClickRemoveBookmark = useCallback(
    async (bookmarkItem: IBookmarkItem) => {
      if (
        isBookmarkListLoaded === true &&
        isBookmarkItemsLoaded === true &&
        bookmarkItem != null
      ) {
        const ret: IBookmarkDeleteItemResponse = await deleteBookmarkItemAPI(
          bookmarkItem.id
        );
        if (ret.success) {
          dispatch(removeBookmarkItem(bookmarkItem));
        }
      }
    },
    [dispatch, isBookmarkListLoaded, isBookmarkItemsLoaded]
  );

  const handleClickSavePaperItem = useCallback(
    async (item: ISearchItem) => {
      const saveSearchState: BookmarkSaveSearchState = {
        bookmarkType: BookmarkType.PAPER,
        searchUrl: "",
        paperId: item.paper_id,
      };

      const bookmarkItem: IBookmarkItem | null = findBookmarkItem(
        saveSearchState,
        id,
        bookmarkItems
      );

      if (bookmarkItem != null) {
        handleClickRemoveBookmark(bookmarkItem);
      }
    },
    [bookmarkItems, handleClickRemoveBookmark, id]
  );

  if (isListExist === false) {
    return (
      <>
        <Head
          title={pageLabels["title"]}
          description={pageLabels["description"]}
        />
        <div
          data-testid="bookmark-list-detail-nolist"
          className="container max-w-6xl m-auto mt-3 mb-20 text-center"
        >
          <p
            className="text-[16px] md:text-xl leading-8 font-bold text-[#085394] mt-6 md:mt-12"
            dangerouslySetInnerHTML={{ __html: pageLabels["empty-message"] }}
          />
        </div>
      </>
    );
  }

  return (
    <>
      <Head
        title={pageLabels["title"].replace("{list-title}", bookmarkListTitle)}
        description={pageLabels["description"]}
      />
      <div
        data-testid="bookmark-list-detail"
        className="container max-w-6xl m-auto mt-3 mb-20 text-center"
      >
        <div className="flex mb-8 justify-items-start">
          <Link href={path.LISTS} legacyBehavior>
            <a
              data-testid="back-link"
              data-test-text={path.LISTS}
              className="inline-flex items-center justify-items-start"
            >
              <Icon size={20} className="mr-2" name="chevron-left" />
              <span className="text-sm text-black">
                {pageLabels["back-to-lists"]}
              </span>
            </a>
          </Link>
        </div>

        {bookmarkListTitle.length > 0 && (
          <div className="flex items-center justify-between">
            <span
              className={classNames(
                "flex flex-1 text-black text-left leading-none items-center mr-5"
              )}
            >
              <div
                className={classNames(
                  "py-2 flex flex-1",
                  "bg-white px-4 rounded-lg",
                  isEditMode ? "flex" : "max-w-[0px] overflow-hidden !p-0"
                )}
              >
                <input
                  ref={listNameRef}
                  type="text"
                  className={classNames(
                    "bg-transparent outline-none text-ellipsis text-[24px] font-bold",
                    "w-full flex-1"
                  )}
                  value={currentEditText}
                  maxLength={BOOKMARK_LISTNAME_MAX_LENGTH}
                  onChange={onChangeListText}
                  onKeyUp={(e) => {
                    if (isEditMode && e.keyCode == 13) {
                      handleClickConfirmEdit(undefined);
                    }
                  }}
                  enterKeyHint="go"
                />
                <div className="flex items-center">
                  <img
                    src={"/icons/x-gray.svg"}
                    className="w-[20px] h-[20px] cursor-pointer"
                    alt="x icon"
                    onClick={handleClickCancelEdit}
                  />

                  <img
                    src={"/icons/check2-green.svg"}
                    className="w-[20px] h-[20px] cursor-pointer ml-3"
                    alt="check2 icon"
                    onClick={() => handleClickConfirmEdit(undefined)}
                  />
                </div>
              </div>
              {isEditMode == false && (
                <div
                  className={classNames(
                    "font-bold break-word",
                    isMobile ? "text-[18px]" : "text-[24px]"
                  )}
                >
                  {bookmarkListTitle}
                </div>
              )}

              {!isEditMode && bookmarkListTitle != BOOKMARK_LISTNAME_FAVORITE && (
                <button className="ml-5" onClick={handleClickEditList}>
                  <Icon size={24} className="text-black" name="edit" />
                </button>
              )}
            </span>

            {bookmarkListTitle != BOOKMARK_LISTNAME_FAVORITE && (
              <button
                className="inline-flex items-center justify-center bg-white rounded-full border border-[#DEE0E3] md:px-5 h-[44px] w-[44px] md:w-auto"
                onClick={handleClickDeleteList}
                disabled={!isBookmarkListLoaded}
              >
                <Icon
                  size={20}
                  className="text-[#C6211F] md:mr-2"
                  name="trash"
                />
                <span className="hidden text-base text-black md:block">
                  {pageLabels["delete-list"]}
                </span>
              </button>
            )}
          </div>
        )}

        <div className="mt-5 md:mt-6">
          <div className="flex space-x-1 bg-transparent border-b border-white">
            <button
              className={classNames(
                "px-10 py-2.5 leading-5 md:w-auto w-full",
                "ring-transparent ring-opacity-60 focus:outline-none focus:ring-2",
                selectedTab == PageTab.PaperTab
                  ? "text-[#000] font-bold border-b-4 border-b-[#57AC91]"
                  : "text-[#707070] border-b-4 border-b-transparent"
              )}
              onClick={() => {
                setSelectedTab(PageTab.PaperTab);
              }}
            >
              {pageLabels["papers"]}
            </button>

            <button
              className={classNames(
                "px-10 py-2.5 leading-5 md:w-auto w-full",
                "ring-transparent ring-opacity-60 focus:outline-none focus:ring-2",
                selectedTab == PageTab.SearchTab
                  ? "text-[#000] font-bold border-b-4 border-b-[#57AC91]"
                  : "text-[#707070] border-b-4 border-b-transparent"
              )}
              onClick={() => {
                setSelectedTab(PageTab.SearchTab);
              }}
            >
              {pageLabels["searches"]}
            </button>
          </div>

          <div className="mt-5">
            {selectedTab == PageTab.PaperTab && (
              <div
                key="paperstab"
                className="min-h-[260px] sm:overflow-y-auto text-left"
              >
                {isBookmarkListLoaded &&
                isBookmarkItemsLoaded &&
                paperNum == 0 ? (
                  <BookmarkEmpty />
                ) : isLoadingPaperDetailItems &&
                  paperDetailItems.length == 0 ? (
                  <LoadingSearchResult />
                ) : (
                  <CardSearchResults
                    onClickCite={handleClickCiteItem}
                    onClickShare={handleClickShareItem}
                    onClickSave={(item: ISearchItem) =>
                      handleClickSavePaperItem(item)
                    }
                    items={paperDetailItems as ISearchItem[]}
                    resultIdToYesNoAnswer={{}}
                  />
                )}
              </div>
            )}

            {selectedTab == PageTab.SearchTab && (
              <div
                key="searchestab"
                className="min-h-[260px] sm:overflow-y-auto"
              >
                {isBookmarkListLoaded &&
                isBookmarkItemsLoaded &&
                searchNum == 0 ? (
                  <BookmarkEmpty />
                ) : (
                  bookmarkListItems.map((bookmarkItem: IBookmarkItem) =>
                    bookmarkItem.bookmark_type == BookmarkType.SEARCH ? (
                      <BookmarkSearchItem
                        key={bookmarkItem.id}
                        bookmarkItem={bookmarkItem}
                        onClickShare={(url: string) => {
                          handleClickShareSearchItem(url);
                        }}
                        onClickRemoveBookmark={() => {
                          handleClickRemoveBookmark(bookmarkItem);
                        }}
                      />
                    ) : null
                  )
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      <ConfirmDeleteListModal
        open={openConfirmDeleteListModal}
        onClose={handleClickCloseConfirmDeleteList}
      />
      <RenameModal
        open={openRenameModal}
        initialLabel={bookmarkListTitle}
        onClose={(value: boolean, newLabel?: string) =>
          handleClickConfirmRenameModal(value, newLabel)
        }
      />

      <ShareModal
        title={shareData.title || searchPageLabels["share-title"]}
        text={shareData.text}
        subText={shareData.subText}
        shareText={shareData.shareText}
        url={shareData.url}
        open={openShare}
        onClose={handleCloseShare}
        isDetail={shareData.isDetail}
        onClickButton={(shareType) => {
          if (shareData.isDetail) {
            executeShareEvent(shareType);
          }
        }}
      />
      <CiteModal
        title={searchPageLabels["cite-title"]}
        apa={citeData.apa}
        bibtex={citeData.bibtex}
        chicago={citeData.chicago}
        mla={citeData.mla}
        harvard={citeData.harvard}
        open={openCite}
        onClose={handleCloseCite}
      />
    </>
  );
};

export const getServerSideProps = withServerSideAuth(async ({ query, req }) => {
  const id = query.id;
  return {
    props: {
      id,
    },
  };
});

export default BookmarkListDetailPage;
