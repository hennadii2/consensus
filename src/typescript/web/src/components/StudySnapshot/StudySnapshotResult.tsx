import { numberWithCommas } from "helpers/format";
import useLabels from "hooks/useLabels";
import React from "react";

interface StudySnapshotResultProps {
  isLocked: boolean;
  isLoading: boolean;
  population?: string | null;
  sampleSize?: number | null;
  studyCount?: number | null;
  methods?: string | null;
  outcomes?: string | null;
}

const BlurWidget = () => (
  <div
    className="absolute left-[-5px] top-0 h-full"
    style={{
      background: "rgba(241, 244, 246, 0.60)",
      width: "calc(100% + 10px)",
      WebkitBackdropFilter: "blur(3px)",
      backdropFilter: "blur(3px)",
    }}
  ></div>
);

const LoadingWidget = ({ className }: { className?: string }) => (
  <div
    data-testid="study-snapshot-loading"
    className={`inline-block h-[10px] w-full rounded-[2px] ${className}`}
    style={{
      background: "#DEE0E3",
    }}
  ></div>
);

function StudySnapshotResult({
  isLocked,
  isLoading,
  population,
  sampleSize,
  studyCount,
  methods,
  outcomes,
}: StudySnapshotResultProps) {
  const [pageLabels] = useLabels("study-snapshot");
  const lockedPopulationStr = "Older adults (50-71 years)";
  const lockedSampleSizeStr = "24";
  const lockedMethodsStr = "Observational";
  const lockedOutcomesStr =
    "memory, task performance, visual performance, completely randomized block design experiment";

  let sampleSizeLabel = pageLabels["sample-size"];
  let sampleSizeValue: string = sampleSize ? sampleSize.toString() : "";
  if (!sampleSize && studyCount) {
    sampleSizeLabel = pageLabels["num-of-studies"];
    sampleSizeValue = studyCount.toString();
  }
  if (!sampleSizeValue) {
    sampleSizeValue = "n/a";
  } else {
    sampleSizeValue = numberWithCommas(sampleSizeValue);
  }

  return (
    <div
      data-testid="study-snapshot-result"
      onClick={(e) => {}}
      className="flex flex-wrap justify-between rounded-[16px] bg-[#F1F4F6] p-[20px]"
    >
      <div className="w-full md:w-[50%] md:border-r md:border-[#DEE0E3] md:pr-[26px] relative">
        <div className="flex items-start">
          <img
            className="w-[20px] h-[20px] mr-[12px] mt-[3px]"
            alt="people"
            src="/icons/people-together.svg"
          />
          <div className="flex-1 md:flex flex-wrap items-baseline">
            <span className="inline-block text-sm text-[#688092] min-w-[95px] md:mr-[8px]">
              {pageLabels["population"]}
            </span>
            <span
              data-testid="population-text"
              className="block md:inline-block text-base text-black relative flex-1"
            >
              {isLoading ? (
                <LoadingWidget />
              ) : (
                <>
                  {isLocked
                    ? lockedPopulationStr
                    : population
                    ? population
                    : "n/a"}
                  {isLocked && <BlurWidget />}
                </>
              )}
            </span>
          </div>
        </div>

        <div className="flex items-start mt-[10px]">
          <img
            className="w-[20px] h-[20px] mr-[12px] mt-[3px]"
            alt="sample"
            src="/icons/sample.svg"
          />
          <div className="flex-1 md:flex flex-wrap items-baseline">
            <span className="inline-block text-sm text-[#688092] min-w-[95px] md:mr-[8px]">
              {sampleSizeLabel}
            </span>
            <span
              data-testid="sample-size-text"
              className="block md:inline-block text-base text-black relative flex-1"
            >
              {isLoading ? (
                <LoadingWidget />
              ) : (
                <>
                  {isLocked ? lockedSampleSizeStr : sampleSizeValue}
                  {isLocked && <BlurWidget />}
                </>
              )}
            </span>
          </div>
        </div>

        <div className="flex items-start mt-[10px]">
          <img
            className="w-[20px] h-[20px] mr-[12px] mt-[3px]"
            alt="analysis"
            src="/icons/analysis.svg"
          />
          <div className="flex-1 md:flex flex-wrap items-baseline">
            <span className="inline-block text-sm text-[#688092] min-w-[95px] md:mr-[8px]">
              {pageLabels["methods"]}
            </span>
            <span
              data-testid="methods-text"
              className="block md:inline-block text-base text-black relative flex-1"
            >
              {isLoading ? (
                <LoadingWidget />
              ) : (
                <>
                  {isLocked ? lockedMethodsStr : methods ? methods : "n/a"}
                  {isLocked && <BlurWidget />}
                </>
              )}
            </span>
          </div>
        </div>
      </div>

      <div className="inline-block md:hidden w-full h-[1px] bg-[#DEE0E3] mt-[16px] mb-[16px]"></div>

      <div className="w-full md:w-[50%] md:pl-[26px]">
        <div className="flex items-start">
          <img
            className="w-[20px] h-[20px] mr-[12px]"
            alt="result"
            src="/icons/result.svg"
          />

          <div className="flex-1">
            <span className="block text-sm text-[#688092] min-w-[75px]">
              {pageLabels["outcomes"]}
            </span>
            <span
              data-testid="outcomes-text"
              className="block text-base text-black relative"
            >
              {isLoading ? (
                <>
                  <LoadingWidget className="mb-[10px]" />
                  <LoadingWidget className="mb-[10px]" />
                  <LoadingWidget className="mb-[10px]" />
                </>
              ) : (
                <>
                  {isLocked ? lockedOutcomesStr : outcomes ? outcomes : "n/a"}
                  {isLocked && <BlurWidget />}
                </>
              )}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default StudySnapshotResult;
