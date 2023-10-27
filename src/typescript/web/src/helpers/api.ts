import axios, { AxiosRequestHeaders } from "axios";
import { PER_PAGE } from "constants/config";
import path from "constants/path";
import { TrackEventData } from "helpers/services/mixpanel/events";
import { IncomingHttpHeaders } from "http";
import { Redirect } from "next";
import requestIp from "request-ip";
import { YesNoType } from "types/YesNoType";
import api, { isServer } from "./apiInstance";
import {
  IBookmarkCreateItemData,
  IBookmarkCreateItemsResponse,
  IBookmarkCreateListResponse,
  IBookmarkDeleteItemResponse,
  IBookmarkDeleteListResponse,
  IBookmarkItemsResponse,
  IBookmarkListResponse,
  IBookmarkUpdateListResponse,
} from "./bookmark";
import { IClerkPublicMetaData } from "./clerk";
import { IEmailRequest } from "./mailchimp";
import { PaymentDetailResponse } from "./stripe";

const REQUEST_TIMEOUT_OPENAI_ENDPOINTS = 400000;
const BASE_URL = isServer() ? process.env.HOST : "/api";

interface RequestHeaderData {
  authToken?: string | null;
  ipAddress?: string;
  headers?: IncomingHttpHeaders;
}

function createRequestHeaders(data?: RequestHeaderData): AxiosRequestHeaders {
  const headers: AxiosRequestHeaders = {};
  if (!data) return headers;

  if (data.authToken) {
    headers["Authorization"] = `Bearer ${data.authToken}`;
  }
  if (data.ipAddress) {
    headers["X-Forwarded-For"] = data.ipAddress;
  }
  if (data.headers) {
    const xApiKey = data.headers["x-api-key"];
    if (xApiKey) {
      headers["X-Api-Key"] = xApiKey.toString();
    }
  }
  return headers;
}

export interface DisputedBadge {
  reason: string;
  url: string;
}

export enum StudyType {
  CASE_STUDY = "case report",
  RCT = "rct",
  SYSTEMATIC_REVIEW = "systematic review",
  META_ANALYSIS = "meta-analysis",
  LITERATURE_REVIEW = "literature review",
  NON_RCT_TRIAL = "non-rct experimental",
  OBSERVATIONAL_STUDY = "non-rct observational study",
  IN_VITRO_TRIAL = "non-rct in vitro",
}

export interface Badges {
  very_rigorous_journal: boolean;
  rigorous_journal: boolean;
  highly_cited_paper: boolean;
  study_type: StudyType | undefined;
  sample_size: number | undefined;
  study_count: number | undefined;
  animal_trial: boolean | undefined;
  large_human_trial: boolean | undefined;
  disputed: DisputedBadge | undefined;
  enhanced: boolean;
}

export interface ClaimDetails {
  id: string;
  text: string;
  url_slug: string;
}

export interface PaperDetails {
  abstract: string;
  abstract_takeaway: string;
  publish_date: string;
  authors: string[];
  badges: Badges;
  citation_count: number;
  doi: string;
  id: string;
  journal: {
    title: string;
    scimago_quartile: number | undefined;
  };
  pages: string;
  provider_url: string;
  title: string;
  volume: string;
  url_slug: string | null;
  year: number;
}

export type PaperDetailsResponse = PaperDetails;

/** Returns details on the given paper id. */
export async function getPaperDetails(
  id: string,
  headerData?: RequestHeaderData,
  queryParams?: string
): Promise<PaperDetailsResponse> {
  let endpoint = `/papers/details/${id}`;
  if (queryParams) {
    endpoint = `${endpoint}?${queryParams}`;
  }

  const { data } = await api.get(endpoint, {
    headers: createRequestHeaders(headerData),
  });

  return data;
}

export interface PapersListResponse {
  paperDetailsListByPaperId: { [key: string]: PaperDetails };
}

export interface GetPapersListOptions {
  includeAbstract: boolean;
  includeJournal: boolean;
  enablePaperSearch: boolean;
}

/** Returns papers list on the given paper ids. */
export async function getPapersList(
  ids: string[],
  options?: GetPapersListOptions | null,
  headerData?: RequestHeaderData
): Promise<PapersListResponse> {
  let endpoint = `/papers/details/?paper_ids=${ids.join(",")}`;

  if (options) {
    endpoint += `&include_abstract=${options.includeAbstract}`;
    endpoint += `&include_journal=${options.includeJournal}`;
    endpoint += `&enable_paper_search=${options.enablePaperSearch}`;
  }

  const { data } = await api.get(endpoint, {
    headers: createRequestHeaders(headerData),
  });

  return data;
}

export interface ClaimDetailsResponse {
  claim: ClaimDetails;
  paper: PaperDetails;
  paperIdForRedirect: string | undefined;
}

/** Returns details on the given claim id. */
export async function getClaimDetails(
  id: string,
  headerData?: RequestHeaderData,
  queryParams?: string
): Promise<ClaimDetailsResponse> {
  let endpoint = `/claims/details/${id}`;
  if (queryParams) {
    endpoint = `${endpoint}?${queryParams}`;
  }

  const { data } = await api.get(endpoint, {
    headers: createRequestHeaders(headerData),
  });

  return data;
}

export interface ClaimDetailsListResponse {
  claimDetailsListByClaimId: { [key: string]: ClaimDetailsResponse };
}

/** Returns details list on the given claim ids. */
export async function getClaimDetailsList(
  ids: string[],
  headerData?: RequestHeaderData
): Promise<ClaimDetailsListResponse> {
  let endpoint = `/claims/details/?claim_ids=${ids.join(",")}`;

  const { data } = await api.get(endpoint, {
    headers: createRequestHeaders(headerData),
  });

  return data;
}

export interface ISearchItem {
  id: string;
  paper_id: string;
  text: string;
  score: number;
  url_slug: string;
  journal: string;
  title: string;
  year: number;
  primary_author: string;
  authors?: string[];
  doi?: string;
  volume: string;
  pages: string;
  badges: Badges;
  citation_count?: number;
}

export interface SearchResponse {
  id: string;
  claims: ISearchItem[];
  isEnd: boolean;
  isYesNoQuestion: boolean | null;
  canSynthesize: boolean | null;
  nuanceRequired: boolean | null;
  canSynthesizeSucceed: boolean | null;
  numTopResults: number | null;
  numRelevantResults: number | null;
}

/** Returns results from a user's search. */
export let searchController = new AbortController();
export async function getClaimSearch(
  query: string,
  pageOffset?: number,
  searchTestingQueryParams?: string,
  headerData?: RequestHeaderData
): Promise<SearchResponse> {
  searchController = new AbortController();
  const page = pageOffset || 0;
  let endpoint = `/search/?query=${encodeURIComponent(
    query
  )}&page=${page}&size=${PER_PAGE}`;

  if (searchTestingQueryParams) {
    endpoint = `${endpoint}${searchTestingQueryParams}`;
  }

  const { data } = await api.get(endpoint, {
    signal: searchController.signal,
    headers: createRequestHeaders(headerData),
  });
  return data;
}

export interface PaperModel {
  doc_id: string;
  paper_id: string;
  display_text: string;
  journal: string;
  title: string;
  primary_author: string;
  authors: string[];
  year: number;
  url_slug: string;
  doi: string;
  volume: string;
  pages: string;
  badges: any;
}

export interface PaperSearchResponse {
  search_id: string;
  papers: PaperModel[];
  isEnd: boolean;
  isYesNoQuestion: boolean | null;
  canSynthesize: boolean | null;
  nuanceRequired: boolean | null;
  canSynthesizeSucceed: boolean | null;
  numTopResults: number | null;
  numRelevantResults: number | null;
}

/** Returns results from a user's paper search. */
export async function getPaperSearch(
  query: string,
  pageOffset?: number,
  searchTestingQueryParams?: string,
  headerData?: RequestHeaderData
): Promise<PaperSearchResponse> {
  searchController = new AbortController();
  const page = pageOffset || 0;
  let endpoint = `/paper_search/?query=${encodeURIComponent(
    query
  )}&page=${page}&size=${PER_PAGE}`;

  if (searchTestingQueryParams) {
    endpoint = `${endpoint}${searchTestingQueryParams}`;
  }

  const { data } = await api.get(endpoint, {
    signal: searchController.signal,
    headers: createRequestHeaders(headerData),
  });
  return data;
}

export async function getSearch(
  enablePaperSearch: boolean,
  query: string,
  pageOffset?: number,
  searchTestingQueryParams?: string,
  headerData?: RequestHeaderData
): Promise<SearchResponse> {
  if (enablePaperSearch) {
    // During migration to v2 paper search, we convert a PaperSearchResponse into
    // a (Claim)SearchRepsonse to maintain compatibility with existing UI.
    const response = await getPaperSearch(
      query,
      pageOffset,
      searchTestingQueryParams,
      headerData
    );
    let claims = response.papers.map((paper) => {
      const claim: ISearchItem = {
        id: paper.paper_id,
        paper_id: paper.paper_id,
        text: paper.display_text,
        score: 0,
        url_slug: paper.url_slug,
        journal: paper.journal,
        title: paper.title,
        year: paper.year,
        primary_author: paper.primary_author,
        authors: paper.authors,
        doi: paper.doi,
        volume: paper.volume,
        pages: paper.pages,
        badges: paper.badges,
      };
      return claim;
    });
    const tmpConvertedClaimSearchResponse: SearchResponse = {
      id: response.search_id,
      claims: claims,
      isEnd: response.isEnd,
      isYesNoQuestion: response.isYesNoQuestion,
      canSynthesize: response.canSynthesize,
      nuanceRequired: response.nuanceRequired,
      canSynthesizeSucceed: response.canSynthesizeSucceed,
      numTopResults: response.numTopResults,
      numRelevantResults: response.numRelevantResults,
    };
    return tmpConvertedClaimSearchResponse;
  } else {
    return await getClaimSearch(
      query,
      pageOffset,
      searchTestingQueryParams,
      headerData
    );
  }
}

export interface YesNoAnswerPercents {
  YES: number;
  NO: number;
  POSSIBLY: number;
}

export interface YesNoResponse {
  resultsAnalyzedCount: number;
  yesNoAnswerPercents: YesNoAnswerPercents;
  resultIdToYesNoAnswer: { [resultId: string]: YesNoType };
  isIncomplete: boolean;
  isDisputed: boolean;
  isSkipped: boolean;
}

/** Returns yes/no results for a search id returned from a getSearch response. */
export async function getYesNoResults(
  searchId: string,
  testingQueryParams?: string,
  headerData?: RequestHeaderData
): Promise<YesNoResponse> {
  let endpoint = `/yes_no/?search_id=${searchId}`;
  if (testingQueryParams) {
    endpoint = `${endpoint}${testingQueryParams}`;
  }
  const { data } = await api.get(endpoint, {
    headers: createRequestHeaders(headerData),
  });
  return data;
}

export interface SummaryResponse {
  resultsAnalyzedCount: number;
  summary?: string;
  isIncomplete: boolean;
  isDisputed: boolean;
  dailyLimitReached: boolean;
}

/** Returns summary results for a search id returned from a getSearch response. */
export async function getSummaryResponse(
  searchId: string,
  testingQueryParams?: string,
  headerData?: RequestHeaderData
): Promise<SummaryResponse> {
  let endpoint = `/summary/?search_id=${searchId}`;
  if (testingQueryParams) {
    endpoint = `${endpoint}${testingQueryParams}`;
  }
  const { data } = await api.get(endpoint, {
    headers: createRequestHeaders(headerData),
    timeout: REQUEST_TIMEOUT_OPENAI_ENDPOINTS,
  });
  return data;
}

export interface StudyDetailsResponse {
  population: string | null;
  method: string | null;
  outcome: string | null;
  dailyLimitReached: boolean;
}

/** Returns study details results for a search id returned from a getSearch response. */
export async function getStudyDetailsResponse(
  id: string,
  testingQueryParams?: string,
  headerData?: RequestHeaderData
): Promise<StudyDetailsResponse> {
  let endpoint = `/study_details/${id}`;
  if (testingQueryParams) {
    endpoint = `${endpoint}${testingQueryParams}`;
  }
  const { data } = await api.get(endpoint, {
    headers: createRequestHeaders(headerData),
    timeout: REQUEST_TIMEOUT_OPENAI_ENDPOINTS,
  });
  return data;
}

export interface AutocompleteResponse {
  queries: string[];
}

/** Returns autocomplete suggestions for the given query. */
export async function getAutocompleteQuerySuggestions(
  query: string,
  testingQueryParams?: string,
  headerData?: RequestHeaderData
): Promise<AutocompleteResponse> {
  let endpoint = `/autocomplete/?query=${encodeURIComponent(query)}`;
  if (testingQueryParams) {
    endpoint = `${endpoint}${testingQueryParams}`;
  }
  const { data } = await api.get(endpoint, {
    headers: createRequestHeaders(headerData),
  });
  return data;
}

export interface TrendingItem {
  key: string;
  title: string;
  queries: string[];
}

interface TrendingResponse {
  queries: string[];
  questionTypes: TrendingItem[];
  topics: TrendingItem[];
  emptyAutocompleteQueries: string[];
}
/** Returns trending queries. */
export async function getTrending(
  headerData?: RequestHeaderData
): Promise<TrendingResponse> {
  const { data } = await api.get(`/trending/queries`, {
    headers: createRequestHeaders(headerData),
  });
  return data;
}

/** Returns the sitemap for the given path. */
export async function getSitemap(
  path: string,
  headerData?: RequestHeaderData
): Promise<string> {
  const { data } = await api.get(`/sitemap/?path=${path}`, {
    headers: createRequestHeaders(headerData),
  });
  return data;
}

/** Returns ip */
export async function getIp(request?: any): Promise<string | undefined> {
  if (!request && isServer()) {
    throw new Error("Calling getIp from server requires passing in request.");
  }
  if (request) {
    return requestIp.getClientIp(request);
  } else {
    const { data } = await api.get("/ip/");
    return data.ip;
  }
}

export function handleRedirect(error: unknown): { redirect: Redirect } {
  let destination = path.INTERNAL_SERVER_ERROR;
  if (axios.isAxiosError(error) && error.response?.status === 429) {
    destination = path.TOO_MANY_REQUESTS;
  }
  return {
    redirect: {
      destination,
      permanent: false,
    },
  };
}

export async function getSubscriptionProductsAPI(
  product_id: string,
  headerData?: RequestHeaderData
): Promise<any> {
  let endpoint = `/subscription_products/`;
  if (product_id) {
    endpoint = `${endpoint}?product_id=${product_id}`;
  }

  const { data } = await api.get(endpoint, {
    headers: createRequestHeaders(headerData),
  });
  return data;
}

export interface StripeCustomerSubscriptionResponse {
  clerk_user_id: string;
  stripe_customer_id: string;
  user_subscription: string;
  org_name: string | null;
}

export async function getCustomerSubscriptionAPI(
  customer_id?: string,
  headerData?: RequestHeaderData
): Promise<StripeCustomerSubscriptionResponse> {
  let endpoint = `/get_stripe_subscription/`;
  if (customer_id) {
    endpoint = `${endpoint}?stripe_customer_id=${customer_id}`;
  }
  const { data } = await api.get(endpoint, {
    headers: createRequestHeaders(headerData),
  });
  return data;
}

export interface StripeAddCustomerSubscriptionResponse {
  subscription_added: boolean;
}

export async function addCustomerSubscriptionAPI(
  stripe_customer_id: string,
  user_subscription: string,
  headerData?: RequestHeaderData
): Promise<StripeAddCustomerSubscriptionResponse> {
  if (isServer()) {
    let endpoint = `/add_stripe_subscription/`;
    const { data } = await api.post(endpoint, {
      stripe_customer_id: stripe_customer_id,
      user_subscription: user_subscription,
      headers: createRequestHeaders(headerData),
    });
    return data;
  } else {
    throw new Error("Calling addCustomerSubscriptionAPI from client requires.");
  }
}

export async function deleteCustomerSubscriptionAPI(
  stripe_customer_id: string,
  headerData?: RequestHeaderData
): Promise<boolean> {
  if (isServer()) {
    let endpoint = `/delete_stripe_subscription/${stripe_customer_id}`;
    const { data } = await api.delete(endpoint, {
      headers: createRequestHeaders(headerData),
    });
    return data;
  } else {
    throw new Error(
      "Calling deleteCustomerSubscriptionAPI from client requires."
    );
  }
}

export async function cancelStripeSubscriptionAPI(): Promise<boolean> {
  const { data } = await api.get(`/subscription_cancel/`);
  return data;
}

export async function resumeStripeSubscriptionAPI(
  subscriptionId: string
): Promise<boolean> {
  const { data } = await api.get(`/subscription_resume/?id=${subscriptionId}`);
  return data;
}

export async function getPaymentMethodDetailAPI(
  payment_method_id: string
): Promise<PaymentDetailResponse> {
  const { data } = await api.get(
    `/get_payment_method/?id=${payment_method_id}`
  );
  return data;
}

export async function getClerkPublicMetaDataAPI(): Promise<IClerkPublicMetaData> {
  let endpoint = `/get_clerk_public_meta_data/`;
  const { data } = await api.get(endpoint);
  return data;
}

export async function updateClerkPublicMetaDataAPI(
  inputData: IClerkPublicMetaData
): Promise<IClerkPublicMetaData> {
  let endpoint = `/update_clerk_public_meta_data/`;
  const { data } = await api.post(endpoint, {
    data: inputData,
  });
  return data;
}

export async function getCustomerPortalLinkAPI(email: string): Promise<string> {
  let endpoint = `/get_customer_portal_link/?email=${email}`;
  const { data } = await api.get(endpoint);
  return data;
}

export async function sendEmailAPI(inputData: IEmailRequest): Promise<boolean> {
  let endpoint = `/send_email/`;
  const { data } = await api.post(endpoint, {
    data: inputData,
  });
  return data;
}

export async function getSearchWithNativeFetch(
  query: string
): Promise<SearchResponse> {
  const endpoint = `/search/?query=${encodeURIComponent(
    query
  )}&page=0&size=${PER_PAGE}`;

  const response = await fetch(BASE_URL + endpoint).then(
    async (res) => await res.json()
  );

  return response;
}

export async function getSummaryResponseWithNativeFetch(
  searchId: string
): Promise<SummaryResponse> {
  const endpoint = `/summary/?search_id=${searchId}`;

  const response = await fetch(BASE_URL + endpoint).then(
    async (res) => await res.json()
  );

  return response;
}

export async function getYesNoResultsWithNativeFetch(
  searchId: string
): Promise<YesNoResponse> {
  const endpoint = `/yes_no/?search_id=${searchId}`;

  const response = await fetch(BASE_URL + endpoint).then(
    async (res) => await res.json()
  );

  return response;
}

/** Track event from NextJS server */
export async function trackEventServerSide(
  data: TrackEventData
): Promise<void> {
  await api.post(`/track_event/`, data);
}

/** Get Bookmark Lists */
export async function getBookmarkListsAPI(
  favoriteListName: string,
  headerData?: RequestHeaderData
): Promise<IBookmarkListResponse> {
  let endpoint = `/bookmarks/lists/?favorite_list_name=${favoriteListName}`;
  const { data } = await api.get(endpoint, {
    headers: createRequestHeaders(headerData),
  });
  return data;
}

/** Create Bookmark List */
export async function createBookmarkListAPI(
  text_label: string,
  headerData?: RequestHeaderData
): Promise<IBookmarkCreateListResponse> {
  let endpoint = `/bookmarks/lists/`;
  const { data } = await api.post(
    endpoint,
    {
      text_label: text_label,
    },
    {
      headers: createRequestHeaders(headerData),
    }
  );
  return data;
}

export async function updateBookmarkListAPI(
  list_id: string,
  text_label: string,
  headerData?: RequestHeaderData
): Promise<IBookmarkUpdateListResponse> {
  let endpoint = `/bookmarks/lists/${list_id}`;
  const { data } = await api.put(
    endpoint,
    {
      text_label: text_label,
    },
    {
      headers: createRequestHeaders(headerData),
    }
  );
  return data;
}

/** Delete Bookmark List */
export async function deleteBookmarkListAPI(
  id: string,
  headerData?: RequestHeaderData
): Promise<IBookmarkDeleteListResponse> {
  let endpoint = `/bookmarks/lists/${id}`;
  const { data } = await api.delete(endpoint, {
    headers: createRequestHeaders(headerData),
  });
  return data;
}

/** Get Bookmark Items */
export async function getBookmarkItemsAPI(
  headerData?: RequestHeaderData
): Promise<IBookmarkItemsResponse> {
  let endpoint = `/bookmarks/items/`;
  const { data } = await api.get(endpoint, {
    headers: createRequestHeaders(headerData),
  });
  return data;
}

/** Create Bookmark Item */
export async function createBookmarkItemsAPI(
  itemsData: IBookmarkCreateItemData[],
  headerData?: RequestHeaderData
): Promise<IBookmarkCreateItemsResponse> {
  let endpoint = `/bookmarks/items/`;
  const { data } = await api.post(
    endpoint,
    {
      items: itemsData,
    },
    {
      headers: createRequestHeaders(headerData),
    }
  );
  return data;
}

/** Delete Bookmark Item */
export async function deleteBookmarkItemAPI(
  id: number,
  headerData?: RequestHeaderData
): Promise<IBookmarkDeleteItemResponse> {
  let endpoint = `/bookmarks/items/${id}`;
  const { data } = await api.delete(endpoint, {
    headers: createRequestHeaders(headerData),
  });
  return data;
}

export default api;

/** Check if any email address has .edu domain */
export async function hasEduEmailDomain(): Promise<boolean> {
  let endpoint = `/has_edu_email_domain/`;
  const { data } = await api.get(endpoint);
  return data;
}
