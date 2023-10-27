import { useUser } from "@clerk/nextjs";
import { withServerSideAuth } from "@clerk/nextjs/ssr";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import CiteModal from "components/CiteModal/CiteModal";
import DetailContent, {
  IDetailItem,
} from "components/DetailContent/DetailContent";
import FindingMissing from "components/FindingMissing";
import Head from "components/Head";
import LoadingDetail from "components/LoadingDetail";
import SaveSearchModal from "components/SaveSearch/SaveSearchModal";
import ShareModal from "components/ShareModal";
import { META_DETAILS_IMAGE } from "constants/config";
import path from "constants/path";
import { FeatureFlag } from "enums/feature-flag";
import { getIp, getPaperDetails, handleRedirect } from "helpers/api";
import {
  BookmarkType,
  findBookmarkItem,
  IBookmarkItem,
  IBookmarkListItem,
  isPaperBookMarked,
} from "helpers/bookmark";
import { extractCitationPage, getCite } from "helpers/cite";
import getFeatureEnabled from "helpers/getFeatureEnabled";
import { paperDetailPagePath, paperDetailPageUrl } from "helpers/pageUrl";
import parseSubText from "helpers/parseSubText";
import { paperDetailSchema } from "helpers/schema";
import { getPaperDetailsParams } from "helpers/testingQueryParams";
import useAnalytics from "hooks/useAnalytics";
import useCite from "hooks/useCite";
import useLabels from "hooks/useLabels";
import useSaveSearch from "hooks/useSaveSearch";
import useShare from "hooks/useShare";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import { GetServerSidePropsContext, NextPage } from "next";
import { useRouter } from "next/router";
import React, { useCallback, useEffect, useState } from "react";
import {
  BookmarkSaveSearchState,
  checkList,
  resetCheckList,
  setBookmarkSaveSearchState,
} from "store/slices/bookmark";

type PaperDetailsPageProps = {
  id: string;
  item?: IDetailItem | null;
};

/**
 * @page Paper Details Page
 * @description Page that has a detailed content data for a paper
 */
const PaperDetailsPage: NextPage<PaperDetailsPageProps> = ({
  item,
  id,
}: PaperDetailsPageProps) => {
  const { query, replace } = useRouter();
  const { isLoaded, isSignedIn, user } = useUser();
  const {
    viewItemEvent,
    clickShareEvent,
    executeShareEvent,
    setAnalyticUser,
    setAnalyticItem,
    clickFullTextLinkEvent,
  } = useAnalytics();
  const [pageLabels] = useLabels("screens.details");
  const dispatch = useAppDispatch();
  const { handleShare, openShare, handleCloseShare } = useShare();
  const { openSaveSearchPopup, handleSaveSearch, handleCloseSaveSearch } =
    useSaveSearch();
  const { handleCite, openCite, handleCloseCite, citeData, setCiteData } =
    useCite();
  const router = useRouter();

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
  const isLimitedBookmarkItem = useAppSelector(
    (state) => state.bookmark.isLimitedBookmarkItem
  );
  const [isBookmarked, setIsBookmarked] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["paper_details", id],
    queryFn: async () => {
      const enablePaperSearch = getFeatureEnabled(
        document.cookie,
        FeatureFlag.PAPER_SEARCH
      );
      if (enablePaperSearch) {
        router.query.enable_paper_search = "true";
      }
      const queryParams = getPaperDetailsParams(router.query);
      const paper = await getPaperDetails(id as string, undefined, queryParams);
      return { paper } as IDetailItem;
    },
    enabled: item === undefined,
    initialData: item,
    onError: (error: unknown) => {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 429) {
          router.push(path.TOO_MANY_REQUESTS);
        } else {
          router.push(path.INTERNAL_SERVER_ERROR);
        }
      }
    },
  });

  const PAGE_TITLE = `${data?.paper.title || ""} - Consensus`;
  const url = paperDetailPageUrl(
    data?.paper.url_slug || "",
    data?.paper.id || ""
  );
  const { firstPage, lastPage } = extractCitationPage(data?.paper.pages);

  // analytic
  useEffect(() => {
    if (item && isLoaded) {
      if (user) {
        setAnalyticUser(user);
      }
      setAnalyticItem(item);
      viewItemEvent();
    }
  }, [item, isLoaded, user, viewItemEvent, setAnalyticItem, setAnalyticUser]);

  // resolve the page at the URL with the correct slug
  useEffect(() => {
    if (query.title && item?.paper?.url_slug) {
      if (query.title !== item.paper.url_slug) {
        replace(paperDetailPagePath(item.paper.url_slug, item.paper.id));
      }
    }
  }, [query, item, replace]);

  const handleClickShare = () => {
    handleShare({
      title: PAGE_TITLE,
      url: window.location.href,
    });

    // analytic
    clickShareEvent();
  };

  const handleClickCite = () => {
    const primaryAuthor =
      data?.paper?.authors && data.paper.authors.length > 0
        ? data?.paper.authors[0]
        : "";

    const { mla, apa, chicago, bibtex, harvard } = getCite({
      authors: data?.paper?.authors,
      author: primaryAuthor,
      journal: data?.paper.journal.title ?? "",
      title: data?.paper.title ?? "",
      year: data?.paper.year ?? 0,
      doi: data?.paper.doi,
      volume: data?.paper.volume,
      pages: data?.paper.pages,
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

  const handleClickFullTextLink = () => {
    // analytic
    clickFullTextLinkEvent();
  };

  useEffect(() => {
    if (data) {
      setIsBookmarked(isPaperBookMarked(data.paper.id, bookmarkItems));
    }
  }, [bookmarkItems, router, data]);

  const handleClickSave = useCallback(async () => {
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

    if (
      isBookmarkItemsLoaded !== true ||
      isBookmarkListLoaded !== true ||
      !data
    ) {
      return;
    }

    if (isLimitedBookmarkItem === true && isBookmarked == false) {
      return;
    }

    const saveSearchState: BookmarkSaveSearchState = {
      bookmarkType: BookmarkType.PAPER,
      searchUrl: "",
      paperId: data.paper ? data.paper.id : "",
    };
    dispatch(setBookmarkSaveSearchState(saveSearchState));
    dispatch(resetCheckList());
    bookmarkLists.forEach((bookmarkList: IBookmarkListItem) => {
      const bookmarkItem: IBookmarkItem | null = findBookmarkItem(
        saveSearchState,
        bookmarkList.id,
        bookmarkItems
      );
      if (bookmarkItem != null) {
        dispatch(checkList(bookmarkList.id));
      }
    });
    handleSaveSearch();
  }, [
    dispatch,
    handleSaveSearch,
    bookmarkLists,
    bookmarkItems,
    isBookmarkItemsLoaded,
    isBookmarkListLoaded,
    data,
    isBookmarked,
    isLimitedBookmarkItem,
    router,
    isSignedIn,
    isLoaded,
  ]);

  return (
    <>
      <Head
        title={PAGE_TITLE}
        schema={paperDetailSchema(data)}
        description={pageLabels["description"].replace(
          "{paper title}",
          data?.paper.title
        )}
        type="article"
        url={url}
        image={META_DETAILS_IMAGE}
        citation={
          data
            ? {
                title: data.paper.title,
                year: data.paper.year,
                journalTitle: data.paper.journal.title,
                doi: data.paper.doi || "",
                publicUrl: url,
                abstractHtmlUrl: data.paper.provider_url,
                abstact: data.paper.abstract,
                authors: data.paper.authors.join(", "),
                volume: data.paper.volume,
                firstPage,
                lastPage,
              }
            : undefined
        }
      />
      <div className="container pt-3 pb-20 sm:pt-6">
        {isLoading ? (
          <div className="mt-5 md:mt-12">
            <LoadingDetail />
          </div>
        ) : data ? (
          <DetailContent
            handleClickCite={handleClickCite}
            handleClickFullTextLink={handleClickFullTextLink}
            handleClickSave={handleClickSave}
            handleClickShare={handleClickShare}
            isBookmarked={isBookmarked}
            isLimitedBookmarkItem={isLimitedBookmarkItem}
            item={data}
          />
        ) : (
          <div className="mb-20">
            <FindingMissing />
          </div>
        )}

        {/* Share */}
        <ShareModal
          open={openShare}
          onClose={handleCloseShare}
          title={pageLabels["share-this-finding"]}
          shareText={pageLabels["share-text"]}
          text={data?.paper?.title || ""}
          subText={parseSubText({
            ...data?.paper,
            journal: data?.paper.journal.title,
          })}
          onClickButton={(shareType) => executeShareEvent(shareType)}
          isDetail
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
      </div>
    </>
  );
};

export const getServerSidePropsDetail = async (
  context: GetServerSidePropsContext
) => {
  try {
    const authToken = await (context.req as any).auth?.getToken();
    const ipAddress = await getIp(context.req);

    const isFromResults = context.req.headers.referer?.includes("/results/");
    const id = context.query.id;
    if (isFromResults) {
      return {
        props: {
          id,
        },
      };
    }

    const enablePaperSearch = getFeatureEnabled(
      context.req.headers.cookie || "",
      FeatureFlag.PAPER_SEARCH
    );
    if (enablePaperSearch) {
      context.query.enable_paper_search = "true";
    }

    const queryParams = getPaperDetailsParams(context.query);
    const paper = await getPaperDetails(
      context.query.id as string,
      {
        authToken,
        ipAddress,
        headers: context.req.headers,
      },
      queryParams
    );

    if (paper?.id) {
      return {
        props: {
          id,
          item: { paper },
        },
      };
    } else {
      return {
        props: {
          id,
          item: null,
        },
      };
    }
  } catch (err) {
    return handleRedirect(err);
  }
};

export const getServerSideProps = withServerSideAuth(getServerSidePropsDetail, {
  loadUser: true,
});

export default PaperDetailsPage;
