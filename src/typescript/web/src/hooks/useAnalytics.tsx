import { UserResource } from "@clerk/types";
import { IDetailItem } from "components/DetailContent/DetailContent";
import { SynthesizeToggleState } from "enums/meter";
import { ISearchItem } from "helpers/api";
import * as googleTagManager from "helpers/services/googleTagManager";
import * as intercom from "helpers/services/intercom";
import * as mixpanel from "helpers/services/mixpanel";
import { useAppDispatch } from "hooks/useStore";
import * as slice from "store/slices/analytic";

declare global {
  interface Window {
    // Adds a quick type to satisfy the type checker.
    dataLayer: any;
  }
}

const useAnalytics = () => {
  const dispatch = useAppDispatch();

  const setAnalyticUser = (user: UserResource) => {
    mixpanel.identifyUser(user);
    const analyticUser: slice.AnalyticUser = {
      id: user.id,
      createdAt: user.createdAt ? new Date(user.createdAt).toISOString() : null,
      lastSignInAt: user.lastSignInAt
        ? new Date(user.lastSignInAt).toISOString()
        : null,
    };
    dispatch(slice.setAnalyticUser(analyticUser));
  };

  const setAnalyticItem = (item: IDetailItem) => {
    dispatch(slice.setAnalyticItem(item));
  };

  const setAnalyticMeta = (meta: {
    query: string;
    page: number;
    index: number;
  }) => {
    dispatch(slice.setAnalyticMeta(meta));
  };

  const setAnalyticSearchItem = (item?: ISearchItem) => {
    dispatch(
      slice.setAnalyticItem(
        item
          ? {
              claim: {
                id: item.id,
                text: item.text,
                url_slug: item.url_slug,
              },
              paper: {
                abstract: "",
                abstract_takeaway: "",
                authors: [item.primary_author],
                badges: item.badges,
                citation_count: 0,
                id: item.paper_id,
                journal: { title: item.journal, scimago_quartile: undefined },
                pages: item.pages,
                provider_url: "",
                title: item.title,
                volume: item.volume,
                url_slug: item.url_slug, //TODO(Jimmy): replace ISearchItem with distinct objects for Papers vs Claims search
                year: item.year,
                publish_date: "",
              },
            }
          : undefined
      )
    );
  };

  const clickFullTextLinkEvent = () => {
    mixpanel.logFullTextClickEvent();
  };

  const viewItemListEvent = (data: {
    items: ISearchItem[];
    page: number;
    query: string;
    isLoadMore: boolean;
  }) => {
    const { items, page, query } = data;
    googleTagManager.logViewItemListEvent(items, page, query);
    // Mixpanel logged server side
  };

  const viewItemEvent = () => {
    googleTagManager.logViewItemEvent();
    // Mixpanel logged server side
  };

  const clickResultItemEvent = (query: string) => {
    mixpanel.logClickResultItemEvent(query);
  };

  const clickShareEvent = () => {
    googleTagManager.logClickShareEvent();
    // Skip logging in mixpanel
  };

  const clickShareResultsEvent = (items: ISearchItem[]) => {
    googleTagManager.logClickShareResultsEvent(items);
    // Skip logging in mixpanel
  };

  const executeShareEvent = (shareType: string) => {
    mixpanel.logExecuteShareClaimEvent(shareType);
    googleTagManager.logExecuteShareEvent(shareType);
  };

  const executeShareResultsEvent = (
    shareType: string,
    items: ISearchItem[],
    query: string
  ) => {
    mixpanel.logShareResultsEvent(shareType, query);
    googleTagManager.logShareResultsEvent(shareType, items, query);
  };

  const searchEvent = (
    query: string,
    isSynthesizeOn?: SynthesizeToggleState
  ) => {
    mixpanel.logSearchEvent(query);
    googleTagManager.logSearchEvent(query);
    intercom.logSearchEvent(query, isSynthesizeOn);
  };

  const logoutEvent = () => {
    googleTagManager.logUserLogoutEvent();
    try {
      mixpanel.logUserLogoutEvent();
    } catch (error) {
      // do nothing
    }
  };

  const loginEvent = (loginMethod: string) => {
    mixpanel.logUserLoginEvent(loginMethod);
    googleTagManager.logUserLoginEvent(loginMethod);
  };

  const signupEvent = (signupMethod: string) => {
    mixpanel.registerUser(signupMethod);
    googleTagManager.logUserSignupEvent(signupMethod);
    // Mixpanel event logged server side
  };

  const pageViewEvent = (data: { route: string; pageTitle: string }) => {
    mixpanel.logPageViewEvent(data);
    googleTagManager.logPageViewEvent(data.route);
  };

  const errorEvent = (message: string) => {
    googleTagManager.logErrorEvent(message);
  };

  return {
    setAnalyticUser,
    setAnalyticMeta,
    setAnalyticItem,
    setAnalyticSearchItem,
    viewItemListEvent,
    viewItemEvent,
    clickShareEvent,
    executeShareEvent,
    searchEvent,
    logoutEvent,
    loginEvent,
    signupEvent,
    clickFullTextLinkEvent,
    clickShareResultsEvent,
    clickResultItemEvent,
    executeShareResultsEvent,
    pageViewEvent,
    errorEvent,
  };
};

export default useAnalytics;
