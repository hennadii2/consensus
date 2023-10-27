export enum MixpanelEvent {
  SearchResultsItemClick = "Results Item Click",
  SearchResultsShare = "Results Share",
  SearchResultsView = "Results View",
  ClaimShare = "Claim Share",
  ClaimView = "Claim View",
  PaperView = "Paper View",
  FullTextClick = "Full Text Click",
  PageView = "Page View",
  PageViewBrowser = "Page View - Browser",
  Search = "Search",
  SignUp = "User Sign Up",
  LogIn = "User Log In",
  LogOut = "User Log Out",
}

export interface MixpanelEventData {
  event: MixpanelEvent;
}

export interface ClaimProperties {
  claimId: string | null;
  claimText: string | null;
  journalName: string | null;
  publishYear: number | null;
  paperTitle: string | null;
  firstAuthor: string | null;
  doi: string | null;
}

export interface PaperProperties {
  paperId: string | null;
  journalName: string | null;
  publishYear: number | null;
  paperTitle: string | null;
  firstAuthor: string | null;
  doi: string | null;
}

export interface ResultProperties {
  pageNumber: number | null;
  resultNumber: number | null;
}

export interface SignUpEvent extends MixpanelEventData {
  event: MixpanelEvent.SignUp;
  authMethod?: string;
  createdAt?: number;
}

/** User views a query's results page, regardless of from a search or direct link. */
interface SearchResultsViewEvent extends MixpanelEventData {
  event: MixpanelEvent.SearchResultsView;
  query: string;
  pageNumber: number;
  isLoadMore: boolean;
}

/** User searches from the search bar. */
interface SearchEvent extends MixpanelEventData {
  event: MixpanelEvent.Search;
  query: string;
}

/** User views a claim details page, regardless of from a search or direct link. */
interface ClaimViewEvent extends MixpanelEventData, ClaimProperties {
  event: MixpanelEvent.ClaimView;
}

/** User views a paper details page, regardless of from a search or direct link. */
interface PaperViewEvent extends MixpanelEventData, PaperProperties {
  event: MixpanelEvent.PaperView;
}

/** User clicks full text link on share page. */
interface FullTextClickEvent extends MixpanelEventData, ClaimProperties {
  event: MixpanelEvent.FullTextClick;
}

/** User clicks one of the 4 share options. */
interface ClaimShareEvent
  extends MixpanelEventData,
    ClaimProperties,
    ResultProperties {
  event: MixpanelEvent.ClaimShare;
  shareType: string;
}

/** User clicks a claim. */
interface SearchResultsItemClickEvent
  extends MixpanelEventData,
    ClaimProperties,
    ResultProperties {
  event: MixpanelEvent.SearchResultsItemClick;
  query: string;
}

/** User shares results. */
interface SearchResultsShareEvent extends MixpanelEventData {
  event: MixpanelEvent.SearchResultsShare;
  shareType: string;
  query: string;
}

/** User succesfully logs out. */
interface LogInEvent extends MixpanelEventData {
  event: MixpanelEvent.LogIn;
  authMethod: string;
}

/** User succesfully logs out. */
interface LogOutEvent extends MixpanelEventData {
  event: MixpanelEvent.LogOut;
}

/** User views a page. */
interface PageViewEvent extends MixpanelEventData {
  event: MixpanelEvent.PageView;
  pageType: string;
  pageTitle: string;
}

export type TrackEventData =
  | SearchResultsViewEvent
  | ClaimViewEvent
  | PaperViewEvent
  | FullTextClickEvent
  | SearchEvent
  | ClaimShareEvent
  | SearchResultsItemClickEvent
  | SearchResultsShareEvent
  | LogOutEvent
  | LogInEvent
  | PageViewEvent;
