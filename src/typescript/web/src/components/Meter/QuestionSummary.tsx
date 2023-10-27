import Tooltip from "components/Tooltip";
import SummaryTooltip from "components/Tooltip/SummaryTooltip/SummaryTooltip";
import { SummaryResponse } from "helpers/api";
import useLabels from "hooks/useLabels";
import React from "react";
import ErrorMeter from "./ErrorMeter";
import IncompleteMeter from "./IncompleteMeter";
import QuestionSummaryFeatureLimited from "./QuestionSummaryFeatureLimited";

interface QuestionSummaryProps {
  data?: SummaryResponse;
  isLoading?: boolean;
  isError?: boolean;
  isIncompleteAll?: boolean;
  isFeatureLimitReached?: boolean;
}

function QuestionSummary({
  data,
  isLoading,
  isError,
  isIncompleteAll,
  isFeatureLimitReached,
}: QuestionSummaryProps) {
  const [summaryLabels] = useLabels("question-summary");
  const summary = data?.summary ?? "";

  const papersAnalyzed = data?.resultsAnalyzedCount;

  return (
    <div>
      <div>
        <div className="flex items-center gap-x-2">
          <p className="text-base md:text-lg font-bold text-black">
            {summaryLabels["summary"]}
          </p>
          <Tooltip
            interactive
            maxWidth={380}
            tooltipContent={<SummaryTooltip />}
          >
            <img
              className="min-w-[20px] max-w-[20px] h-5"
              alt="Info on Consensus Yes/No Meter"
              src="/icons/info.svg"
            />
          </Tooltip>
        </div>
        <div>
          {!isLoading && papersAnalyzed ? (
            <p className="font-normal text-sm text-[#889CAA]">
              {summaryLabels["papers-analyzed"].replace(
                "{count}",
                papersAnalyzed
              )}
            </p>
          ) : null}
        </div>
      </div>
      {isFeatureLimitReached ? (
        <QuestionSummaryFeatureLimited />
      ) : isError ? (
        <div className="mt-4">
          <ErrorMeter message={summaryLabels["error-desc"]} />
        </div>
      ) : !isIncompleteAll && data?.isIncomplete && !isLoading ? (
        <IncompleteMeter />
      ) : data?.dailyLimitReached ? (
        <div className="mt-4">
          <div className="text-sm flex flex-col gap-y-4 bg-[#F8E7E7] text-[#364B44] rounded-lg p-4">
            <p>
              <strong>{summaryLabels["limit"]["title"]}</strong>{" "}
              {summaryLabels["limit"]["desc"]}
            </p>
          </div>
        </div>
      ) : (
        <div>
          <div>
            {isLoading ? (
              <div className="animate-pulse space-y-[10px] mt-3">
                <div className="bg-loading-100 h-3 w-full rounded-sm" />
                <div className="bg-loading-100 h-3 w-[94%] rounded-sm" />
                <div className="bg-loading-100 h-3 w-[98%] rounded-sm" />
                <div className="bg-loading-100 h-3 w-full rounded-sm" />
                <div className="bg-loading-100 h-3 w-[83%] rounded-sm" />
              </div>
            ) : (
              <div className="relative">
                <p className="text-sm mt-3 sm:text-base sm:leading-6 sm:tracking-[0.01em] font-normal text-[#222F2B]">
                  {summary}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default QuestionSummary;
