import { useAuth } from "@clerk/nextjs";
import { MAX_CREDIT_NUM } from "constants/config";
import {
  Badges,
  getStudyDetailsResponse,
  StudyDetailsResponse,
} from "helpers/api";
import { isStudySnapshotEmpty } from "helpers/studyDetail";
import {
  applySubscriptionUsageDataToClerkPublicMetaData,
  isSubscriptionPremium,
} from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  appendStudyPaperId,
  increaseCreditUsageNum,
  setOpenUpgradeToPremiumPopup,
} from "store/slices/subscription";
import StudySnapshotError from "./StudySnapshotError";
import StudySnapshotUpgradePremium from "./StudySnapshotUpgradePremium";

interface StudySnapshotProps {
  paperId: string;
  isDetailPage: boolean;
  badges?: Badges;
}

const DUMMY_VALUE = {
  population: "Adults age 22-45 in the Framingham Heart Study",
  sampleSize: "12,067",
  methods: "Epidemiological analysis of social network data",
  outcomes:
    "Obese BMI chances based on social connections: friends, siblings, and spouses",
};

const LoadingWidget = ({ className }: { className?: string }) => (
  <div
    className={`inline-block h-[10px] w-full rounded-[2px] bg-gray-200 mt-[6px] ${className}`}
  />
);

function StudySnapshotDetail({
  paperId,
  isDetailPage,
  badges,
}: StudySnapshotProps) {
  const [studySnapshotLabel] = useLabels("study-snapshot");
  const dispatch = useAppDispatch();
  const isMobile = useAppSelector((state) => state.setting.isMobile);
  const subscription = useAppSelector(
    (state) => state.subscription.subscription
  );
  const subscriptionUsageData = useAppSelector(
    (state) => state.subscription.usageData
  );
  const { isSignedIn, isLoaded } = useAuth();
  const [isStudySnapshotOpened, setIsStudySnapshotOpened] = useState(false);
  const [isLoadingStudySnapshot, setIsLoadingStudySnapshot] = useState(false);
  const [hasStudyError, setHasStudyError] = useState(false);
  const [shouldUpdateClerkMetaData, setShouldUpdateClerkMetaData] =
    useState(false);
  const initStudyDetailResponse: StudyDetailsResponse = {
    population: null,
    method: null,
    outcome: null,
    dailyLimitReached: false,
  };
  const [isStudySnapshotLimited, setIsStudySnapshotLimited] = useState(false);
  const [isExpandedFirst, setIsExpandedFirst] = useState(false);
  const [studyDetailResponse, setStudyDetailResponse] =
    useState<StudyDetailsResponse>(initStudyDetailResponse);

  useEffect(() => {
    (async () => {
      if (shouldUpdateClerkMetaData) {
        setShouldUpdateClerkMetaData(false);
        if (isLoaded && isSignedIn) {
          applySubscriptionUsageDataToClerkPublicMetaData(
            subscriptionUsageData
          );
        }
      }
    })();
    return () => {};
  }, [shouldUpdateClerkMetaData, subscriptionUsageData, isLoaded, isSignedIn]);

  const onClickUpgradeToPremium = () => {
    dispatch(setOpenUpgradeToPremiumPopup(true));
  };

  const handleClickStudySnapshot = useCallback(async () => {
    if (isLoadingStudySnapshot) return;

    setIsLoadingStudySnapshot(true);
    setHasStudyError(false);
    if (isStudySnapshotOpened == false) {
      setIsStudySnapshotOpened(true);

      const previouslyRunPaperId =
        subscriptionUsageData.studyPaperIds.includes(paperId);
      if (
        !previouslyRunPaperId &&
        !isSubscriptionPremium(subscription) &&
        subscriptionUsageData.creditUsageNum >= MAX_CREDIT_NUM
      ) {
        setIsStudySnapshotLimited(true);
        setIsLoadingStudySnapshot(false);
        return;
      }

      try {
        const studyDetail: StudyDetailsResponse = await getStudyDetailsResponse(
          paperId
        );
        setStudyDetailResponse(studyDetail);

        if (
          isLoaded &&
          isSignedIn == true &&
          !previouslyRunPaperId &&
          !isSubscriptionPremium(subscription) &&
          !isStudySnapshotEmpty(studyDetail, badges)
        ) {
          dispatch(increaseCreditUsageNum());
          dispatch(appendStudyPaperId(paperId));

          setShouldUpdateClerkMetaData(true);
        }
      } catch (error) {
        console.log(error);
        setHasStudyError(true);
      }
    } else {
      setIsStudySnapshotOpened(false);
      setIsStudySnapshotLimited(false);
    }
    setIsLoadingStudySnapshot(false);
  }, [
    dispatch,
    paperId,
    isStudySnapshotOpened,
    isLoadingStudySnapshot,
    setStudyDetailResponse,
    isLoaded,
    isSignedIn,
    subscription,
    subscriptionUsageData,
    badges,
  ]);

  useEffect(() => {
    (async () => {
      if (isExpandedFirst == false) {
        const previouslyRunPaperId =
          subscriptionUsageData.studyPaperIds.includes(paperId);
        if (
          previouslyRunPaperId ||
          (isSubscriptionPremium(subscription) && isDetailPage)
        ) {
          handleClickStudySnapshot();
          setIsExpandedFirst(true);
        }
      }
    })();
    return () => {};
  }, [
    isDetailPage,
    paperId,
    subscription,
    isExpandedFirst,
    subscriptionUsageData,
    handleClickStudySnapshot,
  ]);

  const data = useMemo(() => {
    if (
      isStudySnapshotLimited ||
      isLoadingStudySnapshot ||
      hasStudyError ||
      !studyDetailResponse ||
      !isStudySnapshotOpened
    )
      return null;
    return {
      ...studyDetailResponse,
      method: studyDetailResponse.method || "n/a",
      outcome: studyDetailResponse.outcome || "n/a",
      population: studyDetailResponse.population || "n/a",
    };
  }, [
    studyDetailResponse,
    isStudySnapshotLimited,
    isLoadingStudySnapshot,
    hasStudyError,
    isStudySnapshotOpened,
  ]);

  return (
    <>
      <div className="h-11 rounded-t-2xl py-[10px] flex flex-row items-center justify-center space-x-[6px] bg-gradient-to-l from-[#57AC91] from-31% to-[#8AC3F9] to-162%">
        <img
          className="min-w-[24px] max-w-[24px] h-6 w-6 ml-[12px] mr-[6px] fill-white"
          alt="Sparkler"
          src="/icons/sparkler-white.svg"
        />
        <span className="text-base text-white">
          {studySnapshotLabel["title"]}
        </span>
      </div>
      {hasStudyError ? (
        <div className="px-5 pb-5 pt-4 bg-[#F1F4F6] rounded-b-2xl flex flex-col gap-y-4 relative">
          <StudySnapshotError />
        </div>
      ) : (
        <div className="px-5 pb-5 pt-4 bg-[#F1F4F6] rounded-b-2xl flex flex-col gap-y-4 relative">
          {!isLoadingStudySnapshot && !data && !isStudySnapshotLimited ? (
            <div className="sm:absolute sm:ml-[110px] left-0 bottom-0 top-0 right-0 z-10 flex items-center justify-center">
              <button
                onClick={handleClickStudySnapshot}
                className="flex flex-row gap-x-2 items-center py-[10px] px-4 bg-white border border-[#DEE0E3] rounded-full w-full sm:w-auto justify-center"
              >
                <img
                  className="min-w-[20px] max-w-[20px] w-5"
                  alt="Generate Snapshot"
                  src="/icons/generate-snapshot.svg"
                />
                <span className="text-base text-[#222F2B]">
                  {studySnapshotLabel["generate-snapshot"]}
                </span>
              </button>
            </div>
          ) : null}
          {!isLoadingStudySnapshot && isStudySnapshotLimited ? (
            <div className="sm:absolute sm:ml-[110px] left-0 bottom-0 top-0 right-0 z-10 flex items-center justify-center">
              <button
                onClick={onClickUpgradeToPremium}
                className="flex flex-row gap-x-2 items-center py-[7px] px-5 bg-[#0A6DC2] border border-[#0A6DC2] rounded-full w-full sm:w-auto justify-center"
              >
                <span className="text-sm text-white">
                  {studySnapshotLabel["upgrade-to-premium"]}
                </span>
              </button>
            </div>
          ) : null}
          <div className="flex flex-col items-start justify-start sm:flex-row sm:gap-x-1 sm:gap-y-0 gap-y-1">
            <div className="min-w-[110px] flex flex-row gap-x-[6px] flex-wrap">
              <img
                className="min-w-[20px] max-w-[20px] w-5"
                alt="Population"
                src="/icons/population.svg"
              />
              <span className="text-[#688092] text-sm">
                {studySnapshotLabel["population"]}
              </span>
            </div>
            {isLoadingStudySnapshot ? (
              <LoadingWidget />
            ) : (
              <div
                className={`${
                  data?.population ? "" : "blur"
                } text-[#222F2B] text-base`}
              >
                <span>{data?.population || DUMMY_VALUE.population}</span>
              </div>
            )}
          </div>
          <div className="flex flex-col items-start justify-start sm:flex-row sm:gap-x-1 sm:gap-y-0 gap-y-1">
            <div className="min-w-[110px] flex flex-row gap-x-[6px] flex-wrap">
              <img
                className="min-w-[20px] max-w-[20px] w-5"
                alt="Sample Size"
                src="/icons/sample-size.svg"
              />
              <span className="text-[#688092] text-sm">
                {studySnapshotLabel["sample-size"]}
              </span>
            </div>
            {isLoadingStudySnapshot ? (
              <LoadingWidget />
            ) : (
              <div className={`${data ? "" : "blur"} text-[#222F2B] text-base`}>
                <span>
                  {data
                    ? badges?.sample_size
                      ? badges.sample_size
                      : "n/a"
                    : DUMMY_VALUE.sampleSize}
                </span>
              </div>
            )}
          </div>
          <div className="flex flex-col items-start justify-start sm:flex-row sm:gap-x-1 sm:gap-y-0 gap-y-1">
            <div className="min-w-[110px] flex flex-row gap-x-[6px] flex-wrap">
              <img
                className="min-w-[20px] max-w-[20px] w-5"
                alt="Methods"
                src="/icons/methods.svg"
              />
              <span className="text-[#688092] text-sm">
                {studySnapshotLabel["methods"]}
              </span>
            </div>
            {isLoadingStudySnapshot ? (
              <LoadingWidget />
            ) : (
              <div
                className={`${
                  data?.method ? "" : "blur"
                } text-[#222F2B] text-base`}
              >
                <span>{data?.method || DUMMY_VALUE.methods}</span>
              </div>
            )}
          </div>
          <div className="flex flex-col items-start justify-start sm:flex-row sm:gap-x-1 sm:gap-y-0 gap-y-1">
            <div className="min-w-[110px] flex flex-row gap-x-[6px] flex-wrap">
              <img
                className="min-w-[20px] max-w-[20px] w-5"
                alt="Outcomes"
                src="/icons/outcomes.svg"
              />
              <span className="text-[#688092] text-sm">
                {studySnapshotLabel["outcomes"]}
              </span>
            </div>
            {isLoadingStudySnapshot ? (
              <div className="flex flex-col w-full gap-y-3">
                <LoadingWidget />
                <LoadingWidget />
                <LoadingWidget />
              </div>
            ) : (
              <div
                className={`${
                  data?.outcome ? "" : "blur"
                } text-[#222F2B] text-base`}
              >
                <span>{data?.outcome || DUMMY_VALUE.outcomes}</span>
              </div>
            )}
          </div>
        </div>
      )}
      {isStudySnapshotLimited ? (
        <div className="mt-3">
          <StudySnapshotUpgradePremium isDetail />
        </div>
      ) : null}
    </>
  );
}

export default StudySnapshotDetail;
