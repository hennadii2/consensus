/* eslint-disable react-hooks/exhaustive-deps */
import { useAuth } from "@clerk/clerk-react";
import { withServerSideAuth } from "@clerk/nextjs/ssr";
import { useInfiniteQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import AppliedFilters from "components/AppliedFilters";
import Button, { ClaimButton } from "components/Button";
import ExportButton from "components/Button/ExportButton/ExportButton";
import FilterButton from "components/Button/FilterButton/FilterButton";
import SaveSearchButton from "components/Button/SaveSearchButton/SaveSearchButton";
import { CardSearchResults } from "components/Card";
import CiteModal from "components/CiteModal/CiteModal";
import FilterDrawer from "components/FilterDrawer/FilterDrawer";
import Head from "components/Head";
import LabelRelevantResults from "components/LabelRelevantResults/LabelRelevantResults";
import LoadingSearchResult from "components/LoadingSearchResult";
import Meter from "components/Meter/Meter";
import SynthesizeSwitch from "components/Meter/SynthesizeSwitch";
import NoSearchResult from "components/NoSearchResult";
import SaveSearchModal from "components/SaveSearch/SaveSearchModal";
import ShareModal from "components/ShareModal";
import {
  META_RESULTS_DYNAMIC_IMAGE,
  META_RESULTS_IMAGE,
} from "constants/config";
import path from "constants/path";
import { FeatureFlag } from "enums/feature-flag";
import { SynthesizeToggleState } from "enums/meter";
import {
  getSearch,
  ISearchItem,
  searchController,
  SummaryResponse,
} from "helpers/api";
import {
  BookmarkType,
  findBookmarkItem,
  IBookmarkItem,
  IBookmarkListItem,
  isSearchUrlBookMarked,
} from "helpers/bookmark";
import { getCite } from "helpers/cite";
import getFeatureEnabled from "helpers/getFeatureEnabled";
import {
  getIsMeterFilterActive,
  removedByYesNoMeterFilter,
} from "helpers/meterFilter";
import {
  detailPagePath,
  ResultPageParams,
  resultsPagePath,
  resultsPageUrl,
} from "helpers/pageUrl";
import parseSubText from "helpers/parseSubText";
import getSearchTestingQueryParams from "helpers/search";
import { hashQuery } from "helpers/subscription";
import useAnalytics from "hooks/useAnalytics";
import useCite from "hooks/useCite";
import useLabels from "hooks/useLabels";
import useSaveSearch from "hooks/useSaveSearch";
import useShare from "hooks/useShare";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import flatMap from "lodash/flatMap";
import map from "lodash/map";
import omit from "lodash/omit";
import type { NextPage } from "next";
import { useRouter } from "next/router";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { setCookie } from "react-use-cookie";
import {
  checkList,
  resetCheckList,
  setBookmarkSaveSearchState,
} from "store/slices/bookmark";
import {
  setIsEnd,
  setIsMeterRefresh,
  setIsRefresh,
  setIsSearching,
  setPage,
  setQueryResultData,
} from "store/slices/search";
import { setUseCredit } from "store/slices/subscription";

type SearchProps = {
  enableBookmark?: boolean;
  enablePaperSearch?: boolean;
  enableRelevancyLabels?: boolean;
  isSynthesizeOn?: boolean;
  isTest?: boolean;
};

/**
 * @page Search Page
 * @description page for results
 */
const Search: NextPage<SearchProps> = ({
  isTest,
  isSynthesizeOn,
  enableBookmark,
  enableRelevancyLabels,
  enablePaperSearch,
}: SearchProps) => {
  const router = useRouter();
  const {
    viewItemListEvent,
    clickShareEvent,
    executeShareEvent,
    setAnalyticSearchItem,
    setAnalyticMeta,
    clickShareResultsEvent,
    clickResultItemEvent,
    executeShareResultsEvent,
    errorEvent,
  } = useAnalytics();
  const dispatch = useAppDispatch();
  const isSearching = useAppSelector((state) => state.search.isSearching);
  const queryData = useAppSelector((state) => state.search.queryData);
  const yesNoData = useAppSelector((state) => state.search.yesNoData);
  const isRefresh = useAppSelector((state) => state.search.isRefresh);
  const page = useAppSelector((state) => state.search.page);
  const isEnd = useAppSelector((state) => state.search.isEnd);
  const meterFilter = useAppSelector((state) => state.search.meterFilter);
  const subscription = useAppSelector(
    (state) => state.subscription.subscription
  );
  const subscriptionUsageData = useAppSelector(
    (state) => state.subscription.usageData
  );
  const isLoadedSubscription = useAppSelector(
    (state) => state.subscription.isLoadedSubscription
  );
  const isLoadedUsageData = useAppSelector(
    (state) => state.subscription.isLoadedUsageData
  );
  const [needReRunCheckIfNeedUseCredit, setNeedReRunCheckIfNeedUseCredit] =
    useState(false);
  const [isInitialMountSearch, setIsInitialMountSearch] = useState(true);
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const isMeterFilterActive = getIsMeterFilterActive(meterFilter);
  const [openFilterDrawer, setOpenFilterDrawer] = useState(false);

  const rawQueryText = router.query.q;
  const queryText = Array.isArray(rawQueryText)
    ? rawQueryText.join(" ")
    : rawQueryText || "";

  useEffect(() => {
    if (
      needReRunCheckIfNeedUseCredit &&
      isLoadedSubscription &&
      isLoadedUsageData
    ) {
      setNeedReRunCheckIfNeedUseCredit(false);
      checkIfNeedUseCredit(subscriptionUsageData);
    }
  }, [isLoadedSubscription, isLoadedUsageData, needReRunCheckIfNeedUseCredit]);

  const checkIfNeedUseCredit = async (data: any) => {
    if (isLoadedSubscription == false || isLoadedUsageData == false) {
      setNeedReRunCheckIfNeedUseCredit(true);
      return;
    }

    if (
      subscription.user == null &&
      subscription.org == null &&
      data.synthesizedQueries.includes(hashQuery(router.query.q as string)) ==
        false
    ) {
      dispatch(setUseCredit(false));
    } else {
      dispatch(setUseCredit(true));
    }
  };

  const queryResultKey = [
    "results",
    [
      router.query.q,
      router.query.year_min,
      router.query.study_types,
      router.query.controlled,
      router.query.human,
      router.query.sample_size_min,
      router.query.sjr_min,
      router.query.sjr_max,
      router.query.domain,
    ],
  ];
  const querySummaryKey = [
    "summary",
    queryData.searchId,
    router.query.year_min,
    router.query.study_types,
    router.query.controlled,
    router.query.human,
    router.query.sample_size_min,
    router.query.sjr_min,
    router.query.sjr_max,
    router.query.domain,
  ];

  const questionSummary: SummaryResponse | undefined =
    queryClient.getQueryData(querySummaryKey);

  const {
    data: dataQuery,
    isFetchingNextPage,
    fetchNextPage,
    isLoading,
    remove,
  } = useInfiniteQuery(
    queryResultKey,
    async ({ pageParam = 0 }) => {
      checkIfNeedUseCredit(subscriptionUsageData);

      try {
        const searchQueryParams = getSearchTestingQueryParams(router.query);
        const response = await getSearch(
          enablePaperSearch || false,
          queryText,
          pageParam,
          searchQueryParams
        );

        dispatch(setPage(pageParam));
        dispatch(setIsEnd(response.isEnd));

        viewItemListEvent({
          items: response.claims || [],
          page: pageParam,
          query: queryText,
          isLoadMore: pageParam > 0,
        });

        dispatch(setIsSearching(false));
        return response;
      } catch (error: unknown) {
        dispatch(setIsSearching(false));
        if (axios.isAxiosError(error) && !axios.isCancel(error)) {
          errorEvent(error?.message);
          if (error.response?.status === 429) {
            router.push(path.TOO_MANY_REQUESTS);
          } else {
            router.push(path.INTERNAL_SERVER_ERROR);
          }
        }
        throw error;
      }
    },
    {
      getNextPageParam: (lastPage, pages) => {
        return pages.length;
      },
      // Only refetch cached data whenever the user clicks search or load more,
      // but not during back navigation. This is important for correctly rate
      // limiting users on calls to the backend, and for accurate analytics
      // logging.
      staleTime: isTest ? 0 : Infinity,
      // Don't keep previous data to force loading screen to show when applying
      // date filter.
      keepPreviousData: false,
      enabled: Boolean(router.query),
      onSuccess: () => {
        checkIfNeedUseCredit(subscriptionUsageData);
      },
    }
  );

  const data = useMemo(() => {
    if (isMeterFilterActive) {
      if (dataQuery?.pages.length === 1 && !isFetchingNextPage) {
        fetchNextPage();
      }
      return flatMap(dataQuery?.pages, ({ claims }) =>
        map(claims, (claim) => claim)
      ).filter((claim) => {
        return removedByYesNoMeterFilter(
          meterFilter,
          yesNoData?.resultIdToYesNoAnswer?.[claim.id]
        );
      });
    }
    return flatMap(dataQuery?.pages, ({ claims }) =>
      map(claims, (claim) => claim)
    );
  }, [
    meterFilter,
    yesNoData,
    dataQuery,
    isMeterFilterActive,
    isFetchingNextPage,
  ]);

  const [previousDataQuery, setPreviousDataQuery] = useState<any>(null);
  const [initialMountDataQuery, setInitialMountDataQuery] = useState(true);
  useEffect(() => {
    if (dataQuery != previousDataQuery) {
      setPreviousDataQuery(dataQuery);
      checkIfNeedUseCredit(subscriptionUsageData);
      if (dataQuery?.pages.length === 1) {
        const response = dataQuery.pages[0];
        // Set query level data returned in first page response
        dispatch(
          setQueryResultData({
            searchId: response.id || undefined,
            nuanceRequired: response.nuanceRequired || undefined,
            isYesNoQuestion: response.isYesNoQuestion || undefined,
            canSynthesize: response.canSynthesize || undefined,
            canSynthesizeSucceed: response.canSynthesizeSucceed || undefined,
            numRelevantResults: response.numRelevantResults || undefined,
            numTopResults: response.numTopResults || undefined,
            isEnd: response.isEnd || undefined,
          })
        );
        if (!initialMountDataQuery) {
          dispatch(setIsMeterRefresh(true));
          dispatch(setIsSearching(false));
        }
        setInitialMountDataQuery(false);
      }
    }
  }, [
    dataQuery,
    dispatch,
    subscriptionUsageData,
    previousDataQuery,
    initialMountDataQuery,
  ]);

  const summaryText = useMemo(() => {
    if (isSynthesizeOn && questionSummary?.summary) {
      return questionSummary.summary;
    }
    return;
  }, [questionSummary, isSynthesizeOn]);

  // refresh
  useEffect(() => {
    if (isRefresh && !isInitialMountSearch) {
      dispatch(setIsRefresh(false));
      dispatch(setIsEnd(false));
      remove();
    }
    setIsInitialMountSearch(false);
  }, [isRefresh, dispatch, remove, isInitialMountSearch]);

  const [generalLabels, pageLabels, detailLabels] = useLabels(
    "general",
    "screens.search",
    "screens.details"
  );

  const isActiveFilter = useMemo(() => {
    const { query } = router;
    if (
      query.study_types ||
      query.year_min ||
      query.controlled ||
      query.human ||
      query.sample_size_min ||
      query.sjr_min ||
      query.sjr_max ||
      query.domain
    ) {
      return true;
    }
    return false;
  }, [router.query]);

  const PAGE_TITLE = `${queryText} - Consensus`;
  const total = data.length || 0;
  const isEmpty = !isLoading && !isSearching && total === 0;
  const bookmarkItems: { [key: number]: IBookmarkItem[] } = useAppSelector(
    (state) => state.bookmark.bookmarkItems
  );
  const bookmarkLists: IBookmarkListItem[] = useAppSelector(
    (state) => state.bookmark.bookmarkLists
  );
  const isBookmarkItemsLoaded = useAppSelector(
    (state) => state.bookmark.isBookmarkItemsLoaded
  );
  const isBookmarkListLoaded = useAppSelector(
    (state) => state.bookmark.isBookmarkListLoaded
  );
  const [isBookmarked, setIsBookmarked] = useState(false);

  const { handleShare, openShare, handleCloseShare, shareData, setShareData } =
    useShare();

  const { handleCite, openCite, handleCloseCite, citeData, setCiteData } =
    useCite();

  const { openSaveSearchPopup, handleSaveSearch, handleCloseSaveSearch } =
    useSaveSearch();

  useEffect(() => {
    setIsBookmarked(isSearchUrlBookMarked(router?.asPath, bookmarkItems));
  }, [bookmarkItems, router]);

  // back button listener
  useEffect(() => {
    const handleBack = (e: any) => {
      if (
        e.state?.as === "/search/" ||
        (e.state === null && router.pathname === "/results")
      ) {
        searchController.abort();
        dispatch(setIsSearching(false));
        dispatch(setIsMeterRefresh(true));
      }
    };

    window.addEventListener("popstate", handleBack);

    return () => window.removeEventListener("popstate", handleBack);
  }, [dispatch]);

  // forward button listener
  useEffect(() => {
    const handleForward = (e: any) => {
      if (
        e.state?.as === "/search/" ||
        (e.state === null && router.pathname === "/results")
      ) {
        searchController.abort();
        dispatch(setIsSearching(false));
        dispatch(setIsMeterRefresh(true));
      }
    };

    window.addEventListener("pushstate", handleForward);

    return () => window.removeEventListener("pushstate", handleForward);
  }, [dispatch]);

  const handleLoadMore = () => {
    fetchNextPage();
  };

  const handleClickShare = () => {
    setShareData({
      url: "",
      title: pageLabels["share-title"],
      shareText: pageLabels["share-text"],
      text: queryText,
      subText: "",
      isDetail: false,
    });

    handleShare({
      title: PAGE_TITLE,
      url: window.location.href,
    });

    // analytic
    clickShareResultsEvent(data);
  };

  const handleClickShareItem = (item: ISearchItem, index: number) => {
    const link = detailPagePath(item.url_slug, item.id, enablePaperSearch);
    setShareData({
      url: `${window.location.origin}${link}`,
      title: pageLabels["share-this-finding"],
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
    setAnalyticMeta({ index, page, query: queryText });
    setAnalyticSearchItem(item);
    clickShareEvent();
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

  const handleClickItem = (item: ISearchItem, index: number) => {
    // analytic
    setAnalyticMeta({ index, page, query: queryText });
    setAnalyticSearchItem(item);
    clickResultItemEvent(queryText);
  };

  const handleChangeFilter = async ({
    yearMin,
    studyTypes,
    filterControlledStudies,
    filterHumanStudies,
    sampleSizeMin,
    sjrBestQuartileMax,
    sjrBestQuartileMin,
    fieldsOfStudy,
  }: ResultPageParams) => {
    let params = router.query;
    if (yearMin === generalLabels["all-years"]) {
      params = omit(params, ["year_min"]);
    } else {
      params = {
        ...params,
        yearMin,
      };
    }
    params = {
      ...params,
      studyTypes,
      filterControlledStudies,
      filterHumanStudies,
      sampleSizeMin,
      sjrBestQuartileMin,
      sjrBestQuartileMax,
      fieldsOfStudy,
    };
    await router.replace(resultsPagePath(queryText, params));
  };

  const handleChangeSynthesisToggle = async (value: boolean) => {
    setCookie(
      "synthesize",
      value ? SynthesizeToggleState.ON : SynthesizeToggleState.OFF
    );
    if (!value) {
      await router.replace(
        resultsPagePath(queryText, omit(router.query, ["synthesize"]))
      );
    } else {
      await router.replace(
        resultsPagePath(queryText, {
          ...router.query,
          synthesize: SynthesizeToggleState.ON,
        })
      );
    }
  };

  const getMetaResultImage = useMemo(() => {
    let enableDynamicOpenGraph = false;
    if (router.query.dynamic_open_graph) {
      enableDynamicOpenGraph = true;
    }
    if (
      !enableDynamicOpenGraph ||
      !isSynthesizeOn ||
      (isSynthesizeOn && !queryData.isYesNoQuestion)
    ) {
      return META_RESULTS_IMAGE;
    }
    return META_RESULTS_DYNAMIC_IMAGE + "/" + btoa(queryText);
  }, [isSynthesizeOn, router.query, queryData.isYesNoQuestion]);

  const handleClickSave = useCallback(
    async (
      bookmarkType: BookmarkType,
      searchItem: ISearchItem | null,
      index: number
    ) => {
      if (isBookmarkItemsLoaded !== true || isBookmarkListLoaded !== true) {
        return;
      }

      const saveSearchState = {
        bookmarkType: bookmarkType,
        searchUrl: bookmarkType == BookmarkType.SEARCH ? router?.asPath : "",
        paperId:
          bookmarkType == BookmarkType.SEARCH
            ? ""
            : searchItem != null
            ? searchItem.paper_id
            : "",
      };
      dispatch(setBookmarkSaveSearchState(saveSearchState));
      dispatch(resetCheckList());
      bookmarkLists.forEach((bookmarkList: IBookmarkListItem) => {
        const item: IBookmarkItem | null = findBookmarkItem(
          saveSearchState,
          bookmarkList.id,
          bookmarkItems
        );
        if (item != null) {
          dispatch(checkList(bookmarkList.id));
        }
      });
      handleSaveSearch();
    },
    [
      dispatch,
      router,
      handleSaveSearch,
      bookmarkLists,
      bookmarkItems,
      setBookmarkSaveSearchState,
      isBookmarkItemsLoaded,
      isBookmarkListLoaded,
    ]
  );

  return (
    <>
      <Head
        title={PAGE_TITLE}
        description={pageLabels["description"].replace("{query}", queryText)}
        type="website"
        url={resultsPageUrl(queryText)}
        image={getMetaResultImage}
      />

      <div className="result-content">
        <div className={`container pt-4 pb-10 sm:py-8`}>
          <div className="flex items-center justify-between">
            <SynthesizeSwitch
              canSynthesize={queryData.canSynthesize}
              isLoading={isLoading}
              isSynthesizeOn={isSynthesizeOn}
              isEmpty={isEmpty}
              handleOnChange={handleChangeSynthesisToggle}
            />

            <div className="flex items-center gap-2">
              <FilterButton
                isActiveFilter={isActiveFilter}
                onClick={() => setOpenFilterDrawer(true)}
              />
              {!enableBookmark ? null : (
                <SaveSearchButton
                  dataTestId="save-search"
                  isBookmarked={isBookmarked}
                  disabled={isEmpty}
                  onClick={() => {
                    handleClickSave(BookmarkType.SEARCH, null, 0);
                  }}
                ></SaveSearchButton>
              )}
              <ClaimButton
                dataTestId="share-results"
                onClick={handleClickShare}
                className="w-[44px]"
                disabled={isEmpty}
              >
                <span className="hidden md:block lg:hidden">
                  {pageLabels.share}
                </span>
                <span className="hidden lg:block whitespace-nowrap">
                  {pageLabels["share-search"]}
                </span>
              </ClaimButton>
            </div>
          </div>
          <AppliedFilters
            value={{
              yearMin: router.query.year_min as string,
              studyTypes: router.query.study_types as string,
              filterControlledStudies: router.query.controlled as string,
              filterHumanStudies: router.query.human as string,
              sampleSizeMin: router.query.sample_size_min as string,
              sjrBestQuartileMin: router.query.sjr_min as string,
              sjrBestQuartileMax: router.query.sjr_max as string,
              fieldsOfStudy: router.query.domain as string,
            }}
            onChangeFilter={handleChangeFilter}
          />
          {queryData.canSynthesize && isSynthesizeOn ? (
            <Meter
              isSynthesizeOn={isSynthesizeOn}
              isEmptyResults={isEmpty}
              isLoadingQuery={(isLoading || isSearching) && data.length === 0}
              isTest={isTest}
              querySummaryKey={querySummaryKey}
            />
          ) : null}
          <div>
            {(isLoading || isSearching) && data.length === 0 && (
              <LoadingSearchResult />
            )}
          </div>
          {isEmpty && isMeterFilterActive ? (
            <div className="h-28" />
          ) : isEmpty ? (
            <NoSearchResult />
          ) : (
            <>
              {isLoading || isSearching || !enableRelevancyLabels ? null : (
                <div className="flex items-end">
                  <LabelRelevantResults
                    numRelevantResults={queryData.numRelevantResults}
                    numTopResults={queryData.numTopResults}
                    isEnd={queryData.isEnd}
                  />
                  <ExportButton
                    query={queryText}
                    items={data as ISearchItem[]}
                  />
                </div>
              )}
              <CardSearchResults
                onClickShare={handleClickShareItem}
                onClickItem={handleClickItem}
                onClickCite={handleClickCiteItem}
                onClickSave={(item: ISearchItem, index: number) =>
                  handleClickSave(BookmarkType.PAPER, item, index)
                }
                items={data as ISearchItem[]}
                resultIdToYesNoAnswer={
                  isSynthesizeOn ? yesNoData?.resultIdToYesNoAnswer : {}
                }
                indexLabelMoreResults={
                  enableRelevancyLabels &&
                  queryData.numRelevantResults &&
                  queryData.numRelevantResults > 0 &&
                  queryData.numRelevantResults !== queryData.numTopResults
                    ? queryData.numRelevantResults
                    : undefined
                }
              />
            </>
          )}
          {!isEnd && !isMeterFilterActive && (
            <div className="grid mt-10 place-items-center">
              <Button
                data-testid="loadmore-button"
                onClick={handleLoadMore}
                isLoading={isFetchingNextPage}
                className="text-green-600 bg-white rounded-full py-2 px-6 hover:shadow-[0_2px_4px_0_rgba(189,201,219,0.32)]"
              >
                {generalLabels["load-more"]}
              </Button>
            </div>
          )}
        </div>
      </div>
      <ShareModal
        title={shareData.title || pageLabels["share-title"]}
        text={shareData.text || queryText}
        subText={shareData.subText}
        shareText={shareData.shareText}
        url={shareData.url}
        open={openShare}
        onClose={handleCloseShare}
        isDetail={shareData.isDetail}
        summaryText={summaryText}
        onClickButton={(shareType) => {
          if (shareData.isDetail) {
            executeShareEvent(shareType);
          } else {
            executeShareResultsEvent(shareType, data, queryText);
          }
        }}
      />
      <CiteModal
        title={pageLabels["cite-title"]}
        apa={citeData.apa}
        bibtex={citeData.bibtex}
        chicago={citeData.chicago}
        mla={citeData.mla}
        harvard={citeData.harvard}
        open={openCite}
        onClose={handleCloseCite}
      />

      <SaveSearchModal
        open={openSaveSearchPopup}
        onClose={handleCloseSaveSearch}
      />

      <FilterDrawer
        open={openFilterDrawer}
        onClose={() => setOpenFilterDrawer(false)}
        value={{
          yearMin: router.query.year_min as string,
          studyTypes: router.query.study_types as string,
          filterControlledStudies: router.query.controlled as string,
          filterHumanStudies: router.query.human as string,
          sampleSizeMin: router.query.sample_size_min as string,
          sjrBestQuartileMin: router.query.sjr_min as string,
          sjrBestQuartileMax: router.query.sjr_max as string,
          fieldsOfStudy: router.query.domain as string,
        }}
        onChangeFilter={handleChangeFilter}
      />
    </>
  );
};

export const getServerSideProps = withServerSideAuth(
  async ({ query, req }) => {
    const isSynthesizeOn = query.synthesize === SynthesizeToggleState.ON;

    const enableBookmark = getFeatureEnabled(
      req.headers.cookie || "",
      FeatureFlag.BOOKMARK
    );

    const enableRelevancyLabels = getFeatureEnabled(
      req.headers.cookie || "",
      FeatureFlag.RELEVANCY_LABELS
    );

    const enablePaperSearch = getFeatureEnabled(
      req.headers.cookie || "",
      FeatureFlag.PAPER_SEARCH
    );

    return {
      props: {
        isSynthesizeOn,
        enableBookmark,
        enableRelevancyLabels,
        enablePaperSearch,
      },
    };
  },
  { loadUser: true }
);

export default Search;
