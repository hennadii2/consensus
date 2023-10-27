import { useAuth } from "@clerk/nextjs";
import { SEARCH_ITEM } from "constants/config";
import path from "constants/path";
import { SynthesizeToggleState } from "enums/meter";
import {
  isResultsPageUrl,
  isSearchPageUrl,
  resultsPagePath,
} from "helpers/pageUrl";
import useAnalytics from "hooks/useAnalytics";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import { useRouter } from "next/router";
import { useCallback } from "react";
import { getCookie } from "react-use-cookie";
import { setIsRefresh, setIsSearching } from "store/slices/search";

function useSearch() {
  const router = useRouter();
  const { isSignedIn, isLoaded } = useAuth();
  const isSearching = useAppSelector((state) => state.search.isSearching);
  const dispatch = useAppDispatch();
  const { searchEvent } = useAnalytics();

  const handleSearch = useCallback(
    (value: any) => {
      if (!isLoaded) {
        router?.push(path.INTERNAL_SERVER_ERROR);
        return;
      }

      if (!isSignedIn) {
        const synthesizeState = getCookie("synthesize");
        let isSynthesizeOn =
          synthesizeState === SynthesizeToggleState.ON
            ? SynthesizeToggleState.ON
            : undefined;
        localStorage.setItem(SEARCH_ITEM, value);
        router.push(
          `${path.SIGN_IN}#/?redirect_url=${encodeURIComponent(
            `${window.location.origin}${resultsPagePath(value, {
              synthesize: isSynthesizeOn,
            })}`
          )}`
        );
        return;
      }

      if (value && !isSearching && router) {
        dispatch(setIsSearching(true));

        const synthesizeState = getCookie("synthesize");
        let isSynthesizeOn =
          synthesizeState === SynthesizeToggleState.ON
            ? SynthesizeToggleState.ON
            : undefined;

        searchEvent(value, isSynthesizeOn);

        router.push(
          `${resultsPagePath(value, {
            yearMin: router.query.year_min as string,
            studyTypes: router.query.study_types as string,
            filterControlledStudies: router.query.controlled as string,
            filterHumanStudies: router.query.human as string,
            sampleSizeMin: router.query.sample_size_min as string,
            sjrBestQuartileMin: router.query.sjr_min as string,
            sjrBestQuartileMax: router.query.sjr_max as string,
            fieldsOfStudy: router.query.domain as string,
            synthesize: isSynthesizeOn,
          })}`,
          undefined,
          { shallow: true, scroll: true }
        );

        if (
          value == router.query.q ||
          (isResultsPageUrl(router.route) == false &&
            isSearchPageUrl(router.route) == false)
        ) {
          dispatch(setIsRefresh(true));
        }
      }
    },
    [isLoaded, router, isSignedIn, isSearching, dispatch, searchEvent]
  );
  return { handleSearch, authState: { isSignedIn, isLoaded } };
}

export default useSearch;
