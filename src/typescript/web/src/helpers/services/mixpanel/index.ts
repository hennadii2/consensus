import { UserResource } from "@clerk/types";
import { MIXPANEL_API_KEY, MIXPANEL_PROXY_API_HOST } from "constants/config";
import { trackEventServerSide } from "helpers/api";
import mixpanel from "mixpanel-browser";
import { store } from "../../../store";
import { MixpanelEvent } from "./events";
import { buildClaimProperties, buildResultProperties } from "./util";

let clientSideMixpanelInitialized = false;

/** Initializes mixpanel tracking. */
export function initialize(): void {
  if (MIXPANEL_API_KEY) {
    mixpanel.init(MIXPANEL_API_KEY, {
      debug: false,
      // Our privacy policy states that we do not follow DNT, so ok to disable here
      ignore_dnt: true,
      api_host: MIXPANEL_PROXY_API_HOST,
    });
    clientSideMixpanelInitialized = true;
  }
}

/** Associates all logged events with a custom user id. */
export function identifyUser(user: UserResource): void {
  if (!clientSideMixpanelInitialized) return;
  mixpanel.identify(user.id);
}

/** Adds a custom user and properties to the mixpanel system. */
export function registerUser(signupMethod: string): void {
  if (!clientSideMixpanelInitialized) return;
  const state = store.getState();
  const user = state.analytic.user;
  if (user) {
    // Alias should only be called once when a user signs up.
    mixpanel.alias(user.id);
    mixpanel.people.set_once({
      $name: user.id,
      signUpDate: user.createdAt
        ? new Date(user.createdAt).toISOString()
        : null,
      signUpAuthMethod: signupMethod,
    });
  }
}

/** User views a page. */
export function logPageViewEvent(data: { route: string; pageTitle: string }) {
  trackEventServerSide({
    event: MixpanelEvent.PageView,
    pageType: data.route,
    pageTitle: data.pageTitle,
  });
  // Client side logging of page view (for debugging)
  if (clientSideMixpanelInitialized) {
    mixpanel.track(MixpanelEvent.PageViewBrowser, {
      pageType: data.route,
      pageTitle: data.pageTitle,
    });
  }
}

/** User succesfully logs in. */
export function logUserLoginEvent(authMethod: string) {
  trackEventServerSide({
    event: MixpanelEvent.LogIn,
    authMethod,
  });
}

/** User succesfully logs in. */
export function logUserLogoutEvent() {
  trackEventServerSide({ event: MixpanelEvent.LogOut });
}

/** User searches from the search bar. */
export function logSearchEvent(query: string) {
  trackEventServerSide({
    event: MixpanelEvent.Search,
    query,
  });
}

/** User clicks a claim. */
export function logClickResultItemEvent(query: string) {
  trackEventServerSide({
    event: MixpanelEvent.SearchResultsItemClick,
    query,
    // TODO(meganvw): Pass in all data explicilty rather than relying on redux store
    ...buildClaimProperties(),
    ...buildResultProperties(),
  });
}

/** User clicks one of the 4 share options. */
export function logExecuteShareClaimEvent(shareType: string) {
  trackEventServerSide({
    event: MixpanelEvent.ClaimShare,
    shareType,
    // TODO(meganvw): Pass in all data explicilty rather than relying on redux store
    ...buildClaimProperties(),
    ...buildResultProperties(),
  });
}

/** User shares results. */
export function logShareResultsEvent(shareType: string, query: string) {
  trackEventServerSide({
    event: MixpanelEvent.SearchResultsShare,
    shareType,
    query,
  });
}

/** User clicks full text link on share page. */
export function logFullTextClickEvent() {
  trackEventServerSide({
    event: MixpanelEvent.FullTextClick,
    // TODO(meganvw): Pass in all data explicilty rather than relying on redux store
    ...buildClaimProperties(),
  });
}
