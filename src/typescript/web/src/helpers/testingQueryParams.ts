/**
 * Parses yes/no testing arguments from a URL query and returns a url parameter
 * formatted string to pass to the backend.
 */
export function getYesNoEndpointParams(query?: {
  [key: string]: any;
}): string | undefined {
  if (!query) {
    return "";
  }
  let params = "";
  if (query.synthesize_threshold) {
    const synthesize_threshold =
      query.synthesize_threshold as unknown as number;
    params = `${params}&synthesize_threshold=${synthesize_threshold}`;
  }
  if (query.meter_answer_threshold) {
    const meter_answer_threshold =
      query.meter_answer_threshold as unknown as number;
    params = `${params}&meter_answer_threshold=${meter_answer_threshold}`;
  }
  if (query.meter_force_run) {
    params = `${params}&meter_force_run=true`;
  }
  if (query.cache_off) {
    params = `${params}&cache_off=true`;
  }
  return params;
}

/**
 * Parses autocomplete testing arguments from a URL query and returns a url parameter
 * formatted string to pass to the backend.
 */
export function getAutocompleteEndpointParams(query?: {
  [key: string]: any;
}): string | undefined {
  if (!query) {
    return "";
  }
  let params = "";
  if (query.autocomplete_exact_match) {
    params = `${params}&autocomplete_exact_match=true`;
  }
  if (query.autocomplete_exact_match_better) {
    params = `${params}&autocomplete_exact_match_better=true`;
  }
  if (query.autocomplete_spelling) {
    params = `${params}&autocomplete_spelling=true`;
  }
  if (query.autocomplete_preferred_only) {
    params = `${params}&autocomplete_preferred_only=true`;
  }
  if (query.autocomplete_remove_space) {
    params = `${params}&autocomplete_remove_space=true`;
  }
  if (query.autocomplete_add_space) {
    params = `${params}&autocomplete_add_space=true`;
  }
  if (query.autocomplete_switch_to_exact) {
    const autocomplete_switch_to_exact =
      query.autocomplete_switch_to_exact as unknown as number;
    params = `${params}&autocomplete_switch_to_exact=${autocomplete_switch_to_exact}`;
  }
  if (query.autocomplete_switch_to_exact_words) {
    const autocomplete_switch_to_exact_words =
      query.autocomplete_switch_to_exact_words as unknown as number;
    params = `${params}&autocomplete_switch_to_exact_words=${autocomplete_switch_to_exact_words}`;
  }
  if (query.autocomplete_preferred_boost) {
    const autocomplete_preferred_boost =
      query.autocomplete_preferred_boost as unknown as number;
    params = `${params}&autocomplete_preferred_boost=${autocomplete_preferred_boost}`;
  }
  if (query.autocomplete_words_boost) {
    const autocomplete_words_boost =
      query.autocomplete_words_boost as unknown as number;
    params = `${params}&autocomplete_words_boost=${autocomplete_words_boost}`;
  }
  return params;
}

/**
 * Parses study_details testing arguments from a URL query and returns a url parameter
 * formatted string to pass to the backend.
 */
export function getStudyDetailsEndpointParams(query?: {
  [key: string]: any;
}): string | undefined {
  if (!query) {
    return "";
  }
  let params = "";
  if (query.cache_off) {
    params = `${params}&cache_off=true`;
  }
  return params;
}

/**
 * Parses summary testing arguments from a URL query and returns a url parameter
 * formatted string to pass to the backend.
 */
export function getSummaryEndpointParams(query?: {
  [key: string]: any;
}): string | undefined {
  if (!query) {
    return "";
  }
  let params = "";
  if (query.synthesize_threshold) {
    const synthesize_threshold =
      query.synthesize_threshold as unknown as number;
    params = `${params}&synthesize_threshold=${synthesize_threshold}`;
  }
  if (query.summary_max_results) {
    const summary_max_results = query.summary_max_results as unknown as number;
    params = `${params}&summary_max_results=${summary_max_results}`;
  }
  if (query.summary_daily_limit) {
    const summary_daily_limit = query.summary_daily_limit as unknown as number;
    params = `${params}&summary_daily_limit=${summary_daily_limit}`;
  }
  if (query.cache_off) {
    params = `${params}&cache_off=true`;
  }
  return params;
}

/**
 * Parses claim details page testing arguments from a URL query and returns a url parameter
 * formatted string to pass to the backend.
 */
export function getClaimDetailsParams(query?: {
  [key: string]: any;
}): string | undefined {
  if (!query) {
    return "";
  }
  let params = "";
  if (query.utm_source) {
    const utmSource = query.utm_source as string;
    params = `${params}&utm_source=${utmSource}`;
  }
  if (query.enable_paper_search) {
    params = `${params}&enable_paper_search=true`;
  }
  return params;
}

/**
 * Parses paper details page testing arguments from a URL query and returns a url parameter
 * formatted string to pass to the backend.
 */
export function getPaperDetailsParams(query?: {
  [key: string]: any;
}): string | undefined {
  if (!query) {
    return "";
  }
  let params = "";
  if (query.utm_source) {
    const utmSource = query.utm_source as string;
    params = `${params}&utm_source=${utmSource}`;
  }
  if (query.enable_paper_search) {
    params = `${params}&enable_paper_search=true`;
  }
  return params;
}
