import { PER_PAGE } from "constants/config";
import { store } from "../../../store";
import { ClaimProperties, ResultProperties } from "./events";

export function buildClaimProperties(): ClaimProperties {
  const state = store.getState().analytic;
  const claim = state?.item?.claim || null;
  const journal = state?.item?.paper.journal || null;
  const paper = state?.item?.paper || null;
  return {
    claimId: claim?.id || null,
    claimText: claim?.text || null,
    journalName: journal?.title || null,
    publishYear: paper?.year || null,
    paperTitle: paper?.title || null,
    firstAuthor: paper?.authors.length ? paper.authors[0] : null,
    doi: paper?.doi || null,
  };
}

export function buildResultProperties(): ResultProperties {
  let pageNumber = null;
  let resultNumber = null;

  const state = store.getState().analytic;
  const resultIndex = state && state.index != null ? state.index : null;
  if (resultIndex != null) {
    resultNumber = resultIndex + 1;
    pageNumber = Math.floor(resultIndex / PER_PAGE) + 1;
  }

  return { pageNumber, resultNumber };
}
