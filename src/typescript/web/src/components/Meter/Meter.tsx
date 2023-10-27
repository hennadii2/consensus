import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import Card from "components/Card";
import UseCredits from "components/Subscription/UseCredits/UseCredits";
import DisputedPaperTag from "components/Tag/DisputedPaperTag";
import { MAX_CREDIT_NUM } from "constants/config";
import * as api from "helpers/api";
import { show as showIntercom } from "helpers/services/intercom";
import {
  applySubscriptionUsageDataToClerkPublicMetaData,
  hashQuery,
  isSubscriptionPremium,
} from "helpers/subscription";
import {
  getSummaryEndpointParams,
  getYesNoEndpointParams,
} from "helpers/testingQueryParams";
import useLabels from "hooks/useLabels";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import { useRouter } from "next/router";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  setIsMeterRefresh,
  setSummaryData,
  setYesNoData,
} from "store/slices/search";
import {
  appendSynthesizedQuery,
  setCreditUsageNum,
  setUseCredit,
} from "store/slices/subscription";
import IncompleteMeter from "./IncompleteMeter";
import NuanceRequired from "./NuanceRequired";
import QuestionSummary from "./QuestionSummary";
import YesNoMeter from "./YesNoMeter";

type Props = {
  isTest?: boolean;
  isEmptyResults?: boolean;
  isSynthesizeOn: boolean;
  isLoadingQuery: boolean;
  querySummaryKey: (string | string[] | undefined)[];
};

const Meter = (props: Props) => {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const [meterLabels] = useLabels("meter");
  const subscription = useAppSelector(
    (state) => state.subscription.subscription
  );
  const useCredit = useAppSelector((state) => state.subscription.useCredit);
  const isMeterRefresh = useAppSelector((state) => state.search.isMeterRefresh);
  const isMobile = useAppSelector((state) => state.setting.isMobile);
  const queryData = useAppSelector((state) => state.search.queryData);
  const summaryData = useAppSelector((state) => state.search.summaryData);
  const yesNoData = useAppSelector((state) => state.search.yesNoData);
  const [isMeterLimited, setIsMeterLimited] = useState(false);
  const [isSummaryLimited, setIsSummaryLimited] = useState(false);
  const subscriptionUsageData = useAppSelector(
    (state) => state.subscription.usageData
  );
  const { isSignedIn, isLoaded } = useAuth();
  const isPremium = isSubscriptionPremium(subscription);
  const previouslySynthesizedQuery =
    subscriptionUsageData.synthesizedQueries.includes(
      hashQuery(router.query.q as string)
    );
  const [isDecreasedCreditNum, setIsDecreasedCreditNum] = useState(false);

  const updateClerkPublicMetaData = useCallback(async () => {
    if (!props.isTest && isLoaded && isSignedIn) {
      applySubscriptionUsageDataToClerkPublicMetaData(subscriptionUsageData);
    }
  }, [subscriptionUsageData, props.isTest, isLoaded, isSignedIn]);

  const isNotEnoughPredictions = useMemo(() => {
    return (
      !queryData.numRelevantResults ||
      Boolean(
        queryData.numRelevantResults && queryData.numRelevantResults < 5
      ) ||
      Boolean(
        yesNoData?.resultIdToYesNoAnswer &&
          Object.keys(yesNoData.resultIdToYesNoAnswer).length < 5
      )
    );
  }, [queryData.numRelevantResults, yesNoData?.resultIdToYesNoAnswer]);

  const yesNoQuery = useQuery(
    [
      "meter",
      queryData.searchId,
      router.query.year_min,
      router.query.study_types,
      router.query.controlled,
      router.query.human,
      router.query.sample_size_min,
      router.query.sjr_min,
      router.query.sjr_max,
      router.query.domain,
    ],
    async () => {
      if (!queryData.searchId) {
        return undefined;
      }
      if (isLoaded && isSignedIn == true) {
        if (
          !previouslySynthesizedQuery &&
          !isPremium &&
          subscriptionUsageData.creditUsageNum >= MAX_CREDIT_NUM &&
          queryData.canSynthesizeSucceed
        ) {
          setIsMeterLimited(true);
          return undefined;
        }
      }

      setIsDecreasedCreditNum(false);
      const yesNoParams = getYesNoEndpointParams(router.query);
      const res = await api.getYesNoResults(
        queryData.searchId,
        yesNoParams,
        undefined
      );
      if (
        isLoaded &&
        isSignedIn == true &&
        !previouslySynthesizedQuery &&
        !isPremium
      ) {
        const successfulMeter = res && !res.isIncomplete;
        if (successfulMeter && isDecreasedCreditNum == false) {
          dispatch(setCreditUsageNum(subscriptionUsageData.creditUsageNum + 1));
          dispatch(appendSynthesizedQuery(hashQuery(router.query.q as string)));
          setIsDecreasedCreditNum(true);
        }
      }
      dispatch(setYesNoData(res));
      return res;
    },
    {
      enabled:
        !props.isLoadingQuery &&
        props.isSynthesizeOn &&
        Boolean(queryData.searchId) &&
        Boolean(queryData.isYesNoQuestion) &&
        Boolean(queryData.canSynthesize) &&
        Boolean(!queryData.nuanceRequired) &&
        ((isLoaded && isSignedIn == false) || useCredit === true),
      staleTime: props.isTest ? 0 : Infinity,
      keepPreviousData: false,
      onSuccess: () => {
        updateClerkPublicMetaData();
      },
    }
  );

  const questionSummaryQuery = useQuery(
    props.querySummaryKey,
    async () => {
      if (!queryData.searchId) {
        return undefined;
      }
      if (isLoaded && isSignedIn == true) {
        if (
          !previouslySynthesizedQuery &&
          !isPremium &&
          subscriptionUsageData.creditUsageNum >= MAX_CREDIT_NUM &&
          queryData.canSynthesizeSucceed
        ) {
          setIsSummaryLimited(true);
          return undefined;
        }
      }

      setIsDecreasedCreditNum(false);
      const params = getSummaryEndpointParams(router.query);
      const res = await api.getSummaryResponse(
        queryData.searchId,
        params,
        undefined
      );
      const successfulSummary = res && !res.isIncomplete;
      if (
        isLoaded &&
        isSignedIn == true &&
        !previouslySynthesizedQuery &&
        successfulSummary &&
        !isPremium
      ) {
        if (isDecreasedCreditNum == false) {
          dispatch(setCreditUsageNum(subscriptionUsageData.creditUsageNum + 1));
          dispatch(appendSynthesizedQuery(hashQuery(router.query.q as string)));
          setIsDecreasedCreditNum(true);
        }
      }

      dispatch(setSummaryData(res));
      return res;
    },
    {
      enabled:
        !props.isLoadingQuery &&
        props.isSynthesizeOn &&
        Boolean(queryData.searchId) &&
        Boolean(queryData.canSynthesize) &&
        Boolean(!queryData.nuanceRequired) &&
        ((isLoaded && isSignedIn == false) || useCredit === true),
      staleTime: props.isTest ? 0 : Infinity,
      keepPreviousData: false,
      onSuccess: () => {
        updateClerkPublicMetaData();
      },
    }
  );

  // refresh
  const [isInitialMountRefresh, setIsInitialMountRefresh] = useState(true);
  useEffect(() => {
    (async () => {
      if (isMeterRefresh && !isInitialMountRefresh) {
        dispatch(setIsMeterRefresh(false));
        yesNoQuery?.remove();
        questionSummaryQuery?.remove();
      }
      setIsInitialMountRefresh(false);
    })();
    return () => {};
  }, [
    dispatch,
    isMeterRefresh,
    yesNoQuery,
    questionSummaryQuery,
    isInitialMountRefresh,
  ]);

  const checkCredit =
    useCredit === false &&
    queryData.canSynthesizeSucceed &&
    !queryData.nuanceRequired;
  const isIncompleteAll =
    (yesNoQuery.data?.isIncomplete &&
      questionSummaryQuery.data?.isIncomplete) ||
    (!queryData.isYesNoQuestion && questionSummaryQuery.data?.isIncomplete) ||
    (!queryData.canSynthesizeSucceed && !checkCredit);
  const isDisputed =
    yesNoQuery.data?.isDisputed || questionSummaryQuery.data?.isDisputed;

  if (checkCredit) {
    const userOutOfCredits =
      !isPremium && subscriptionUsageData.creditUsageNum >= MAX_CREDIT_NUM;

    if (!userOutOfCredits) {
      dispatch(setUseCredit(true));
    }
  }

  return (
    <div>
      <Card className="relative mt-4 !p-0 overflow-hidden rounded-xl md:rounded-2xl">
        <div
          style={{
            background:
              "linear-gradient(269.37deg, #57AC91 -30.69%, #8AC3F9 162.6%)",
          }}
          className="p-1 md:p-[6px] h-[31px] flex justify-center items-center text-white flex-nowrap"
        >
          <div className="text-[#57AC91] bg-[#ffffffd9] text-xs !rounded-[4px] font-bold px-2 py-0.5 mr-1 md:mr-2">
            beta
          </div>
          <p className="text-xs md:text-sm truncate md:flex leading-[18px]">
            {isMobile
              ? meterLabels["beta"]["first-short"]
              : meterLabels["beta"]["first"]}
            <span className="hidden md:block ml-1">
              {meterLabels["beta"]["second"]}{" "}
              <a
                onClick={() => {
                  showIntercom();
                }}
                className="font-semibold cursor-pointer"
              >
                {meterLabels["beta"]["here"]}
              </a>
            </span>
          </p>
        </div>
        <div className="relative grid grid-cols-1 md:grid-cols-2">
          <div className="p-5 md:px-8 md:pt-4 md:pb-8">
            <QuestionSummary
              data={summaryData}
              isLoading={
                (questionSummaryQuery.isLoading &&
                  questionSummaryQuery.fetchStatus !== "idle") ||
                props.isLoadingQuery
              }
              isError={questionSummaryQuery.isError}
              isIncompleteAll={isIncompleteAll}
              isFeatureLimitReached={
                isSummaryLimited && previouslySynthesizedQuery === false
              }
            />
          </div>
          <div className="md:hidden border-[#D3EAFD] border-t mx-6 "></div>
          <YesNoMeter
            data={yesNoData}
            isLoading={
              (yesNoQuery.isLoading && yesNoQuery.fetchStatus !== "idle") ||
              props.isLoadingQuery
            }
            isYesNoQuestion={queryData.isYesNoQuestion}
            isIncompleteAll={isIncompleteAll}
            isError={yesNoQuery.isError}
            isNotEnoughPredictions={isNotEnoughPredictions}
            isFeatureLimitReached={
              isMeterLimited && previouslySynthesizedQuery === false
            }
          />
          {isIncompleteAll && (
            <div className="absolute flex justify-center w-full items-center h-full bg-[#ffffffba] px-5">
              <div className="max-w-md">
                <IncompleteMeter isIncompleteAll />
              </div>
            </div>
          )}
          {queryData.nuanceRequired && !props?.isEmptyResults && (
            <div className="absolute flex justify-center w-full items-center h-full bg-[#ffffffba] px-5">
              <div className="max-w-md">
                <NuanceRequired />
              </div>
            </div>
          )}
        </div>
        {checkCredit && subscriptionUsageData.isSet && (
          <div className="absolute flex justify-center w-full items-center h-full bg-[#ffffffba] px-5 top-0">
            <div className="max-w-[460px] w-full">
              <UseCredits />
            </div>
          </div>
        )}
      </Card>
      {isDisputed && (
        <div data-testid="meter-disputed">
          <Card className="flex px-4 py-3 rounded-xl mt-4 items-center gap-3 flex-wrap">
            <DisputedPaperTag tooltip={meterLabels["disputed-tooltip"]} />
            <p className="text-[#CF031A]">{meterLabels["disputed"]}</p>
          </Card>
        </div>
      )}
    </div>
  );
};

export default Meter;
