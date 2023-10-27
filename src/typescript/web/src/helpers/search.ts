/**
 * Parses search testing arguments from a URL query and returns a url parameter
 * formatted string to pass to the backend.
 */
function getSearchTestingQueryParams(query?: {
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
  if (query.relevancy_threshold) {
    const relevancy_threshold = query.relevancy_threshold as unknown as number;
    params = `${params}&relevancy_threshold=${relevancy_threshold}`;
  }
  if (query.method) {
    const method = query.method as string;
    params = `${params}&method=${method}`;
  }
  if (query.stopwords) {
    const stopwords = query.stopwords as string;
    params = `${params}&stopwords=${stopwords}`;
  }
  if (query.punctuation) {
    const punctuation = query.punctuation as string;
    params = `${params}&punctuation=${punctuation}`;
  }
  if (query.boost1) {
    const boost1 = query.boost1 as unknown as number;
    params = `${params}&boost1=${boost1}`;
  }
  if (query.boost2) {
    const boost2 = query.boost2 as unknown as number;
    params = `${params}&boost2=${boost2}`;
  }
  if (query.rescore_count) {
    const rescore_count = query.rescore_count as unknown as number;
    params = `${params}&rescore_count=${rescore_count}`;
  }
  if (query.sort) {
    const sort = query.sort as string;
    params = `${params}&sort=${sort}`;
  }
  if (query.qa_page_count) {
    const qa_page_count = query.qa_page_count as string;
    params = `${params}&qa_page_count=${qa_page_count}`;
  }
  if (query.cache_off) {
    params = `${params}&cache_off=true`;
  }
  if (query.extract_answers_model) {
    const model_override = query.extract_answers_model as string;
    params = `${params}&extract_answers_model=${model_override}`;
  }
  if (query.synthesize_statements) {
    params = `${params}&synthesize_statements=true`;
  }
  return params;
}

function getFilterParams(query?: { [key: string]: any }): string | undefined {
  if (!query) {
    return "";
  }
  let params = "";
  // String filters
  if (query.study_types) {
    const study_types = query.study_types as string;
    params = `${params}&study_types=${study_types}`;
  }
  if (query.domain) {
    // Fields of study
    const domain = query.domain as string;
    params = `${params}&domain=${domain}`;
  }
  // Boolean filters
  if (query.controlled) {
    params = `${params}&controlled=true`;
  }
  if (query.human) {
    params = `${params}&human=true`;
  }
  // Range filters
  if (query.year_min) {
    const year_min = query.year_min as string;
    params = `${params}&year_min=${year_min}`;
  }
  if (query.year_max) {
    const year_max = query.year_max as string;
    params = `${params}&year_max=${year_max}`;
  }
  if (query.sample_size_min) {
    const sample_size_min = query.sample_size_min as string;
    params = `${params}&sample_size_min=${sample_size_min}`;
  }
  if (query.sample_size_max) {
    const sample_size_max = query.sample_size_max as string;
    params = `${params}&sample_size_max=${sample_size_max}`;
  }
  if (query.sjr_min) {
    const sjr_min = query.sjr_min as string;
    params = `${params}&sjr_min=${sjr_min}`;
  }
  if (query.sjr_max) {
    const sjr_max = query.sjr_max as string;
    params = `${params}&sjr_max=${sjr_max}`;
  }
  return params;
}

export default function getSearchEndpointParams(query?: {
  [key: string]: any;
}): string | undefined {
  const filterParams = getFilterParams(query);
  const searchTestingParams = getSearchTestingQueryParams(query);
  return `${filterParams}${searchTestingParams}`;
}
