import {
  getSearchFiltersFromParam,
  TFilter,
} from "components/AppliedFilters/AppliedFilters";
import { WEB_URL } from "constants/config";

export function searchPagePath(): string {
  return `/search/`;
}

export function searchPageUrl(): string {
  return `${WEB_URL}${searchPagePath()}`;
}

export interface ResultPageParams {
  synthesize?: string;
  // String filters
  studyTypes?: string;
  fieldsOfStudy?: string;
  // Bool filters
  filterControlledStudies?: string;
  filterHumanStudies?: string;
  // Range filters
  sampleSizeMin?: string;
  sampleSizeMax?: string;
  sjrBestQuartileMin?: string;
  sjrBestQuartileMax?: string;
  yearMin?: string;
  yearMax?: string;
}

export function resultsPagePath(
  query: string,
  params?: ResultPageParams
): string {
  let path = `/results/?q=${encodeURIComponent(query)}`;

  if (params?.synthesize) {
    path += `&synthesize=${params?.synthesize}`;
  }
  // String filters
  if (params?.studyTypes) {
    path += `&study_types=${params?.studyTypes}`;
  }
  if (params?.fieldsOfStudy) {
    path += `&domain=${params?.fieldsOfStudy}`;
  }
  // Bool filters
  if (params?.filterControlledStudies) {
    path += `&controlled=${params?.filterControlledStudies}`;
  }
  if (params?.filterHumanStudies) {
    path += `&human=${params?.filterHumanStudies}`;
  }
  // Range filters
  if (params?.sampleSizeMin) {
    path += `&sample_size_min=${params?.sampleSizeMin}`;
  }
  if (params?.sampleSizeMax) {
    path += `&sample_size_max=${params?.sampleSizeMax}`;
  }
  if (params?.sjrBestQuartileMin) {
    path += `&sjr_min=${params?.sjrBestQuartileMin}`;
  }
  if (params?.sjrBestQuartileMax) {
    path += `&sjr_max=${params?.sjrBestQuartileMax}`;
  }
  if (params?.yearMin) {
    path += `&year_min=${params?.yearMin}`;
  }
  if (params?.yearMax) {
    path += `&year_max=${params?.yearMax}`;
  }

  return path;
}

export function resultsPageUrl(
  query: string,
  params?: ResultPageParams
): string {
  return `${WEB_URL}${resultsPagePath(query, params)}`;
}

export function isSearchPageUrl(url: string): boolean {
  if (url && (url == "/" || url.startsWith("/search"))) {
    return true;
  }
  return false;
}

export function isResultsPageUrl(url: string): boolean {
  if (url && url.startsWith("/results")) {
    return true;
  }
  return false;
}

export function isDetailsPageUrl(url: string): boolean {
  if (url && url.startsWith("/details/")) {
    return true;
  }
  return false;
}

export function isBookmarkListsPageUrl(url: string): boolean {
  if (url && url.startsWith("/lists")) {
    return true;
  }
  return false;
}

export function isSubscriptionPageUrl(url: string): boolean {
  if (url && url.startsWith("/subscription")) {
    return true;
  }
  return false;
}

export function paperDetailPagePath(slug: string, id: string): string {
  return `/papers/${encodeURIComponent(slug)}/${id}/`;
}

export function paperDetailPageUrl(slug: string, id: string): string {
  return `${WEB_URL}${paperDetailPagePath(slug, id)}`;
}

export function claimDetailPagePath(slug: string, id: string): string {
  return `/details/${encodeURIComponent(slug)}/${id}/`;
}

export function claimDetailPageUrl(slug: string, id: string): string {
  return `${WEB_URL}${claimDetailPagePath(slug, id)}`;
}

export function detailPagePath(
  slug: string,
  id: string,
  enablePaperSearch = false
): string {
  return enablePaperSearch
    ? paperDetailPagePath(slug, id)
    : claimDetailPagePath(slug, id);
}

export function pricingPageUrl(price_id?: string): string {
  let path = `${WEB_URL}/pricing/`;
  if (price_id) {
    path += `?price_id=${price_id}`;
  }
  return path;
}

export function subscriptionPageUrl(action?: string): string {
  let path = `${WEB_URL}/subscription`;
  if (action) {
    path += `?action=${action}`;
  }
  return path;
}

export function bookmarkListDetailPagePath(id: string): string {
  return `/lists/${id}/`;
}

export function getSearchTextFromResultUrl(url: string): string {
  if (url == null) return "";
  let q = "";
  let final_text = "",
    final_parameter_text = "";
  const indexResults = url.indexOf("/results/?");
  if (indexResults == -1) return "";

  const urlSearchParams = new URLSearchParams(url.substring(indexResults + 10));

  q = urlSearchParams.get("q") ?? "";
  if (q == "") return "";
  final_text = q;

  const filters: TFilter[] = getSearchFiltersFromParam({
    yearMin: urlSearchParams.get("year_min") as string,
    studyTypes: urlSearchParams.get("study_types") as string,
    filterControlledStudies: urlSearchParams.get("controlled") as string,
    filterHumanStudies: urlSearchParams.get("human") as string,
    sampleSizeMin: urlSearchParams.get("sample_size_min") as string,
    sjrBestQuartileMin: urlSearchParams.get("sjr_min") as string,
    sjrBestQuartileMax: urlSearchParams.get("sjr_max") as string,
    fieldsOfStudy: urlSearchParams.get("domain") as string,
  });

  filters.map(
    (filter, filterIdx) =>
      (final_parameter_text +=
        (final_parameter_text == "" ? "" : ", ") + filter.label)
  );

  if (final_parameter_text != "") {
    final_text += " - " + final_parameter_text;
  }
  return final_text;
}
