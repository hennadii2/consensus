import { useAuth } from "@clerk/nextjs";
import Icon from "components/Icon";
import Tooltip from "components/Tooltip";
import StudyDetailsTooltip from "components/Tooltip/StudyDetailsTooltip/StudyDetailsTooltip";
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
import React, { useCallback, useEffect, useState } from "react";
import {
  appendStudyPaperId,
  increaseCreditUsageNum,
} from "store/slices/subscription";
import StudySnapshotError from "./StudySnapshotError";
import StudySnapshotResult from "./StudySnapshotResult";
import StudySnapshotUpgradePremium from "./StudySnapshotUpgradePremium";

interface StudySnapshotProps {
  paperId: string;
  isDetailPage: boolean;
  badges?: Badges;
}

function StudySnapshot({ paperId, isDetailPage, badges }: StudySnapshotProps) {
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
    badges,
    isStudySnapshotOpened,
    isLoadingStudySnapshot,
    setStudyDetailResponse,
    isLoaded,
    isSignedIn,
    subscription,
    subscriptionUsageData,
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

  return (
    <>
      {isMobile && (
        <button
          data-testid="snapshot-header-button"
          className="inline-flex items-center"
          onClick={(e) => {}}
        >
          <span
            className="inline-flex w-[24px] h-[24px] rounded-full border border-[#889CAA] justify-center items-center"
            onClick={(e) => {
              handleClickStudySnapshot();
            }}
          >
            {isStudySnapshotOpened ? (
              <Icon
                size={18}
                name="chevron-up"
                strokeWidth={1}
                color={"#222F2B"}
              />
            ) : (
              <Icon
                size={18}
                name="chevron-down"
                strokeWidth={1}
                color={"#222F2B"}
              />
            )}
          </span>

          <Tooltip
            interactive
            maxWidth={334}
            tooltipContent={<StudyDetailsTooltip />}
          >
            <>
              <img
                className="min-w-[24px] max-w-[24px] h-6 w-6 ml-[12px] mr-[6px]"
                alt="Sparkler"
                src="/icons/sparkler.svg"
              />

              <span className="text-base text-black">
                {studySnapshotLabel["title"]}
              </span>
            </>
          </Tooltip>
        </button>
      )}

      {!isMobile && (
        <Tooltip
          interactive
          maxWidth={334}
          tooltipContent={<StudyDetailsTooltip />}
        >
          <button
            data-testid="snapshot-header-button"
            className="inline-flex items-center"
            onClick={(e) => {
              handleClickStudySnapshot();
            }}
          >
            <span className="inline-flex w-[24px] h-[24px] rounded-full border border-[#889CAA] justify-center items-center">
              {isStudySnapshotOpened ? (
                <Icon
                  size={18}
                  name="chevron-up"
                  strokeWidth={1}
                  color={"#222F2B"}
                />
              ) : (
                <Icon
                  size={18}
                  name="chevron-down"
                  strokeWidth={1}
                  color={"#222F2B"}
                />
              )}
            </span>

            <img
              className="min-w-[24px] max-w-[24px] h-6 w-6 ml-[12px] mr-[6px]"
              alt="Sparkler"
              src="/icons/sparkler.svg"
            />

            <span className="text-base text-black">
              {studySnapshotLabel["title"]}
            </span>
          </button>
        </Tooltip>
      )}

      {isStudySnapshotOpened && (
        <div data-testid="snapshot-expanded-widget">
          <div className="mt-[12px] md:mb-0">
            {hasStudyError ? (
              <StudySnapshotError />
            ) : (
              <StudySnapshotResult
                isLocked={isStudySnapshotLimited}
                isLoading={isLoadingStudySnapshot}
                population={studyDetailResponse.population}
                methods={studyDetailResponse.method}
                outcomes={studyDetailResponse.outcome}
                sampleSize={badges?.sample_size ? badges.sample_size : null}
                studyCount={badges?.study_count ? badges.study_count : null}
              />
            )}
          </div>
          {isStudySnapshotLimited && (
            <div className="mt-[12px]">
              <StudySnapshotUpgradePremium />
            </div>
          )}
        </div>
      )}
    </>
  );
}

export default StudySnapshot;
