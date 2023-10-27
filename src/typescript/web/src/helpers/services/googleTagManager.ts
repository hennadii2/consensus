import { PER_PAGE } from "constants/config";
import { ISearchItem } from "helpers/api";
import { store } from "../../store";

function buildUser() {
  const state = store.getState();
  const user = state.analytic.user;
  return user
    ? {
        user_id: user.id,
        registration_timestamp: user.createdAt
          ? new Date(user.createdAt).getTime().toString()
          : "",
        last_login_timestamp: user.lastSignInAt
          ? new Date(user.lastSignInAt).getTime().toString()
          : "",
      }
    : null;
}

function buildItem(type: string, more?: { [key: string]: string }) {
  const state = store.getState();
  const item = state.analytic.item;
  const pageState = state.analytic.page;
  const queryState = state.analytic.query;
  const indexState = state.analytic.index;

  if (!item) {
    return null;
  }

  return {
    item_id: item.claim?.id || item.paper.id,
    item_name: item.claim?.text.substring(0, 100), //TODO(Jimmy) If no claim, add paper key takeaway once populated
    quantity: 1,
    item_brand: item.paper.journal.title,
    item_variant: "claim",
    item_category: item.paper.authors[0],
    item_category2: String(item.paper.year),
    item_category3: item.paper.title,
    item_category4: item.paper.doi,
    item_list_name: queryState,
    price: pageState + 1,
    index: indexState + 1,
    currency: "USD",
    coupon: type,
    ...(more || {}),
  };
}

function pushToDataLayer(values: any) {
  try {
    window.dataLayer?.push(values);
  } catch (error) {
    /** supress errors */
  }
}

function clearEcommerce() {
  pushToDataLayer({
    ecommerce: null,
  });
}

export function logViewItemListEvent(
  items: ISearchItem[],
  page: number,
  query: string
) {
  clearEcommerce();
  pushToDataLayer({
    event: "view_item_list",
    user_properties: buildUser(),
    ecommerce: {
      items: items.map((item, index) => ({
        item_id: item.id,
        item_name: item.text.substring(0, 100),
        quantity: 1,
        item_brand: item.journal,
        item_variant: "claim",
        item_category: item.primary_author,
        item_category2: String(item.year),
        item_category3: item.title,
        item_category4: item.doi,
        item_list_name: query,
        price: page + 1,
        index: page * PER_PAGE + index + 1,
        currency: "USD",
        coupon: "view_results_v1",
      })),
    },
  });
}

export function logViewItemEvent() {
  clearEcommerce();
  pushToDataLayer({
    event: "view_item",
    user_properties: buildUser(),
    ecommerce: {
      items: [buildItem("view_details_v1")],
    },
  });
}

export function logClickShareEvent() {
  clearEcommerce();
  pushToDataLayer({
    event: "add_to_cart",
    user_properties: buildUser(),
    ecommerce: {
      items: [buildItem("clicks_share_v1")],
    },
  });
}

export function logClickShareResultsEvent(items: ISearchItem[]) {
  const state = store.getState();
  const queryState = state.analytic.query;

  clearEcommerce();
  window.dataLayer?.push({
    event: "add_to_cart",
    user_properties: buildUser(),
    ecommerce: {
      items: items.map((item, index) => ({
        item_id: item.id,
        item_name: item.text.substring(0, 100),
        quantity: 1,
        item_brand: item.journal,
        item_variant: "claim",
        item_category: item.primary_author,
        item_category2: String(item.year),
        item_category3: item.title,
        item_category4: item.doi,
        item_list_name: queryState,
        price: 1,
        index: index + 1,
        currency: "USD",
        coupon: "clicks_share_results_v1",
      })),
    },
  });
}

export function logExecuteShareEvent(shareType: string) {
  clearEcommerce();
  pushToDataLayer({
    event: "begin_checkout",
    user_properties: buildUser(),
    ecommerce: {
      items: [buildItem("executes_share_v1", { item_category5: shareType })],
    },
  });
}

export function logShareResultsEvent(
  shareType: string,
  items: ISearchItem[],
  query: string
) {
  clearEcommerce();
  window.dataLayer?.push({
    event: "begin_checkout",
    user_properties: buildUser(),
    ecommerce: {
      items: items.map((item, index) => ({
        item_id: item.id,
        item_name: item.text.substring(0, 100),
        quantity: 1,
        item_brand: item.journal,
        item_variant: "claim",
        item_category: item.primary_author,
        item_category2: String(item.year),
        item_category3: item.title,
        item_category4: item.doi,
        item_list_name: query,
        price: 1,
        index: index + 1,
        currency: "USD",
        coupon: "executes_share_results_v1",
        item_category5: shareType,
      })),
    },
  });
}

export function logSearchEvent(query: string) {
  pushToDataLayer({
    event: "search",
    search_term: query,
    user_properties: buildUser(),
  });
}

export function logUserLogoutEvent() {
  pushToDataLayer({
    event: "logout",
    user_properties: buildUser(),
  });
}

export function logUserLoginEvent(loginMethod: string) {
  pushToDataLayer({
    event: "login",
    login_method: loginMethod,
    user_properties: buildUser(),
  });
}

export function logUserSignupEvent(signupMethod: string) {
  pushToDataLayer({
    event: "signup",
    signup_method: signupMethod,
    user_properties: buildUser(),
  });
}

export function logPageViewEvent(page: string) {
  pushToDataLayer({
    page,
    event: "page_view",
    user_properties: buildUser(),
  });
}

export function logErrorEvent(message: string) {
  pushToDataLayer({
    event: "error",
    message,
    user_properties: buildUser(),
  });
}
