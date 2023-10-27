import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import classNames from "classnames";
import BetaTag from "components/BetaTag";
import Button from "components/Button";
import Logo from "components/Logo";
import SearchInput from "components/SearchInput";
import { PremiumFeatureModal } from "components/Subscription";
import {
  BOOKMARK_LISTNAME_FAVORITE,
  BOOKMARK_MAX_CUSTOM_LIST_NUM,
  BOOKMARK_MAX_ITEM_NUM,
  MAX_MOBILE_WIDTH,
} from "constants/config";
import path from "constants/path";
import {
  getBookmarkItemsAPI,
  getBookmarkListsAPI,
  searchController,
} from "helpers/api";
import {
  getBookmarkItemsCount,
  IBookmarkItemsResponse,
  IBookmarkListResponse,
} from "helpers/bookmark";
import {
  isBookmarkListsPageUrl,
  isDetailsPageUrl,
  isResultsPageUrl,
  isSubscriptionPageUrl,
} from "helpers/pageUrl";
import {
  getActiveSubscription,
  getSubscriptionUsageData,
} from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useRouter } from "next/router";
import React, { useCallback, useEffect, useState } from "react";
import {
  setBookmarkItems,
  setBookmarkLists,
  setIsLimitedBookmarkItem,
  setIsLimitedBookmarkList,
} from "store/slices/bookmark";
import { setIsSearching } from "store/slices/search";
import { setSettingIsMobile } from "store/slices/setting";
import {
  setIsLoadedSubscription,
  setIsLoadedUsageData,
  setSubscription,
  setSubscriptionUsageData,
} from "store/slices/subscription";
import BookmarkButton from "./BookmarkButton";
import UserButton from "./UserButton";
const HelpButton = dynamic(() => import("./HelpButton"), {
  ssr: false,
});

type TopBarProps = {
  hasSearch?: boolean;
  hasHelp?: boolean;
  hasBookmark?: boolean;
};

/**
 * @component TopBar
 * @description TopBar component to all of the pages.
 * @example
 * return (
 *   <TopBar hasSearch />
 * )
 */
const TopBar = ({ hasSearch, hasHelp, hasBookmark }: TopBarProps) => {
  const router = useRouter();
  const [generalLabels] = useLabels("general");
  const { isSignedIn, isLoaded } = useAuth();
  const dispatch = useAppDispatch();
  const [hideIcon, setHideIcon] = useState(false);
  const [isRunningSubscriptionQuery, setIsRunningSubscriptionQuery] =
    useState(false);
  const subscription = useAppSelector(
    (state) => state.subscription.subscription
  );
  const isLoadedSubscription = useAppSelector(
    (state) => state.subscription.isLoadedSubscription
  );
  const isLoadedUsageData = useAppSelector(
    (state) => state.subscription.isLoadedUsageData
  );
  const isBookmarkListLoaded = useAppSelector(
    (state) => state.bookmark.isBookmarkListLoaded
  );
  const isBookmarkItemsLoaded = useAppSelector(
    (state) => state.bookmark.isBookmarkItemsLoaded
  );
  const bookmarkLists = useAppSelector((state) => state.bookmark.bookmarkLists);
  const bookmarkItems = useAppSelector((state) => state.bookmark.bookmarkItems);
  const [enableBookmarkQuery, setEnableBookmarkQuery] = useState(false);

  useEffect(() => {
    setEnableBookmarkQuery(
      Boolean(
        isResultsPageUrl(router.route) ||
          isDetailsPageUrl(router.route) ||
          isSubscriptionPageUrl(router.route) ||
          isBookmarkListsPageUrl(router.route)
      )
    );
  }, [router]);

  const handleClickHome = () => {
    searchController.abort();
    dispatch(setIsSearching(false));
  };

  const getSubscriptionTopBarQuery = useQuery(
    ["get-user-subscription-topbar"],
    async () => {
      if (isRunningSubscriptionQuery == false) {
        setIsRunningSubscriptionQuery(true);
        dispatch(setIsLoadedSubscription(false));
        dispatch(setIsLoadedUsageData(false));

        const subscriptionRet = await getActiveSubscription({});
        dispatch(setSubscription(subscriptionRet));

        try {
          const data = await getSubscriptionUsageData(subscriptionRet);
          dispatch(setSubscriptionUsageData(data));
        } catch (error) {}

        setIsRunningSubscriptionQuery(false);
        dispatch(setIsLoadedSubscription(true));
        dispatch(setIsLoadedUsageData(true));
      }
    }
  );

  const getBookmarkQuery = useQuery(
    ["get-bookmark-topbar"],
    async () => {
      if (!hasBookmark) {
        // Skip network calls if bookmarks are not enabled
        return;
      }

      try {
        const retList: IBookmarkListResponse = await getBookmarkListsAPI(
          BOOKMARK_LISTNAME_FAVORITE
        );
        if (retList != null && retList.bookmark_lists) {
          dispatch(setBookmarkLists(retList.bookmark_lists));
        }
      } catch (error) {}

      try {
        const retItems: IBookmarkItemsResponse = await getBookmarkItemsAPI();
        if (retItems != null && retItems.bookmark_items) {
          dispatch(setBookmarkItems(retItems.bookmark_items));
        }
      } catch (error) {}
    },
    {
      enabled: enableBookmarkQuery,
    }
  );

  useEffect(() => {
    if (isLoadedSubscription && isBookmarkListLoaded) {
      if (
        subscription.org != null ||
        subscription.user != null ||
        bookmarkLists.length <= BOOKMARK_MAX_CUSTOM_LIST_NUM
      ) {
        dispatch(setIsLimitedBookmarkList(false));
      } else {
        dispatch(setIsLimitedBookmarkList(true));
      }
    }

    const bookmarkItemNum = getBookmarkItemsCount(bookmarkItems);
    if (isLoadedSubscription && isBookmarkItemsLoaded) {
      if (
        subscription.org != null ||
        subscription.user != null ||
        bookmarkItemNum < BOOKMARK_MAX_ITEM_NUM
      ) {
        dispatch(setIsLimitedBookmarkItem(false));
      } else {
        dispatch(setIsLimitedBookmarkItem(true));
      }
    }
  }, [
    dispatch,
    subscription,
    isLoadedSubscription,
    isBookmarkListLoaded,
    isBookmarkItemsLoaded,
    bookmarkLists,
    bookmarkItems,
  ]);

  useEffect(() => {
    if (hasSearch) {
      const handleScroll = () => {
        if (hasSearch) {
          if (window.innerWidth > 900) {
            setHideIcon(false);
          } else if (window.scrollY > 50) {
            setHideIcon(true);
          } else if (window.scrollY === 0) {
            setHideIcon(false);
          }
        }
      };

      window.addEventListener("scroll", handleScroll);

      return () => {
        window.removeEventListener("scroll", handleScroll);
      };
    }
  }, [hasSearch]);

  const settingIsMobile = useCallback(() => {
    dispatch(setSettingIsMobile(window.innerWidth < MAX_MOBILE_WIDTH));
  }, [dispatch]);

  useEffect(() => {
    settingIsMobile();
    addEventListener("resize", (event) => {
      settingIsMobile();
    });
  }, [settingIsMobile]);

  const redirect = `/#/?redirect_url=${
    [path.SIGN_IN, path.SIGN_UP].includes(router?.route) ? "" : router?.asPath
  }`;

  return (
    <div
      data-testid="topbar"
      className={classNames("flex flex-col", !hasSearch && "py-2")}
    >
      <div className="flex items-start md:items-center md:justify-between flex-col md:flex-row w-full relative">
        <div
          className="flex items-center gap-4"
          style={{ marginTop: hideIcon ? -64 : 0, transition: "0.4s" }}
        >
          <Link href="/search" passHref legacyBehavior>
            <a onClick={handleClickHome} style={{ height: 42, width: 42 }}>
              <Logo size="small" hasBackground />
            </a>
          </Link>
          <div className="absolute left-14">
            <BetaTag text />
          </div>
        </div>
        {hasSearch && (
          <div className="flex-1 w-full md:w-auto mt-4 md:mt-0 md:mr-14">
            <SearchInput large />
          </div>
        )}
        <div
          style={{ marginTop: hideIcon ? -64 : 0, transition: "0.4s" }}
          className="absolute right-0 flex items-center"
        >
          {isLoaded && !isSignedIn ? (
            <Link href={`${path.SIGN_UP}${redirect}`} passHref legacyBehavior>
              <a className="text-[#085394] font-bold text-base">
                {generalLabels["signup"]}
              </a>
            </Link>
          ) : null}
          {hasBookmark && isSignedIn && <BookmarkButton />}
          {hasHelp && isSignedIn && <HelpButton isSignedIn={isSignedIn} />}
          {isLoaded ? (
            isSignedIn ? (
              <UserButton />
            ) : (
              <Link href={`${path.SIGN_IN}${redirect}`} passHref legacyBehavior>
                <a>
                  <Button className="ml-3 h-11" variant="primary">
                    Sign In
                  </Button>
                </a>
              </Link>
            )
          ) : null}
        </div>
      </div>

      {<PremiumFeatureModal />}
    </div>
  );
};

export default TopBar;
