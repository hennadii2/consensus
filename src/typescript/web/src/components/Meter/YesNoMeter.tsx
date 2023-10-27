import Tag from "components/Tag";
import Tooltip from "components/Tooltip";
import MeterTooltip from "components/Tooltip/MeterTooltip/MeterTooltip";
import { EXAMPLE_QUERY_IN_METER } from "constants/config";
import { YesNoResponse } from "helpers/api";
import { defaultMeterFilter } from "helpers/meterFilter";
import { setSynthesizeOn } from "helpers/setSynthesizeOn";
import useLabels from "hooks/useLabels";
import useSearch from "hooks/useSearch";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import React, { useEffect, useState } from "react";
import { setMeterFilter } from "store/slices/search";
import { MeterFilterParams } from "types/MeterFilterParams";
import ErrorMeter from "./ErrorMeter";
import IncompleteMeter from "./IncompleteMeter";
import YesNoMeterFeatureLimited from "./YesNoMeterFeatureLimited";

type Props = {
  data?: YesNoResponse;
  isLoading?: boolean;
  isError?: boolean;
  isYesNoQuestion?: boolean;
  isIncompleteAll?: boolean;
  isFeatureLimitReached?: boolean;
  isNotEnoughPredictions?: boolean;
};

function YesNoMeter({
  data,
  isLoading,
  isYesNoQuestion,
  isIncompleteAll,
  isError,
  isFeatureLimitReached,
  isNotEnoughPredictions,
}: Props) {
  const [meterLabels] = useLabels("meter");
  const papersAnalyzed = data?.resultsAnalyzedCount || 0;
  const [isEnableMeterFilter, setIsEnableMeterFilter] = useState(false);
  const { handleSearch } = useSearch();

  const dispatch = useAppDispatch();
  const meterFilter = useAppSelector((state) => state.search.meterFilter);

  useEffect(() => {
    return () => {
      dispatch(setMeterFilter(defaultMeterFilter));
    };
  }, [dispatch]);

  const handleMeterFilter = () => {
    setIsEnableMeterFilter(!isEnableMeterFilter);
    if (isEnableMeterFilter) {
      dispatch(
        setMeterFilter({
          no: true,
          possibly: true,
          yes: true,
        })
      );
    }
  };

  const handleMeterFilterItem = (params: MeterFilterParams) => {
    dispatch(setMeterFilter(params));
  };

  return (
    <div className="px-6 pt-4 pb-[34px] md:px-8 md:pb-8 md:border-l border-[#D3EAFD]">
      <div className="flex justify-between items-start">
        <div className="flex-col">
          <div data-testid="meter" className="flex items-center gap-x-2">
            <p className="text-base md:text-lg font-bold text-black md:w-36">
              Consensus Meter
            </p>
            <Tooltip
              interactive
              maxWidth={380}
              tooltipContent={<MeterTooltip />}
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
              <p className="font-normal text-sm sm:leading-[1.375rem] text-[#889CAA]">
                {papersAnalyzed} {meterLabels["papers-analyzed"]}
              </p>
            ) : null}
          </div>
        </div>

        {!isFeatureLimitReached && (
          <button
            onClick={handleMeterFilter}
            className={`w-8 h-8 rounded-[4px] items-center justify-center flex -mr-1 ${
              isEnableMeterFilter ? "border border-[#0A6DC2]" : ""
            }`}
          >
            <img
              alt="filter"
              src={
                isEnableMeterFilter ? "/icons/filter2.svg" : "/icons/filter.svg"
              }
              className="w-5 h-5"
            />
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="animate-pulse space-y-5 mt-3">
          <div className="items-center flex">
            <div className="bg-loading-100 h-[14px] w-[14px] rounded-full mr-2" />
            <div className="bg-loading-200 h-4 w-[79px] rounded-md mr-[20px]" />
            <div className="bg-loading-100 h-4 flex-1 rounded-md" />
          </div>
          <div className="items-center flex">
            <div className="bg-loading-100 h-[14px] w-[14px] rounded-full mr-2" />
            <div className="bg-loading-200 h-4 w-[79px] rounded-md mr-[20px]" />
            <div className="bg-loading-100 h-4 flex-1 rounded-md" />
          </div>
          <div className="items-center flex">
            <div className="bg-loading-100 h-[14px] w-[14px] rounded-full mr-2" />
            <div className="bg-loading-200 h-4 w-[79px] rounded-md mr-[20px]" />
            <div className="bg-loading-100 h-4 flex-1 rounded-md" />
          </div>
        </div>
      ) : !isIncompleteAll && !isYesNoQuestion ? (
        <div className="text-sm flex flex-col gap-y-2 bg-[#F1F4F6] text-[#364B44] rounded-lg p-4 text-center items-center mt-4">
          <p>
            <strong>{meterLabels["is-not-question"]["not-enough"]}</strong>{" "}
            {meterLabels["is-not-question"]["try-asking"]}
          </p>
          <Tag
            q={EXAMPLE_QUERY_IN_METER}
            onClick={(event) => {
              event.preventDefault();
              setSynthesizeOn();
              handleSearch(EXAMPLE_QUERY_IN_METER);
            }}
          >
            e.g. {EXAMPLE_QUERY_IN_METER}
          </Tag>
        </div>
      ) : !isIncompleteAll && (isNotEnoughPredictions || data?.isIncomplete) ? (
        <div className="mt-4 ">
          <IncompleteMeter />
        </div>
      ) : isFeatureLimitReached ? (
        <YesNoMeterFeatureLimited />
      ) : isError ? (
        <div className="mt-4 ">
          <ErrorMeter />
        </div>
      ) : (
        <div className="flex flex-col gap-y-3 mt-3 text-sm sm:leading-[1.375rem] text-[#688092]">
          <div className="md:flex items-center">
            <p className="w-[129px] flex items-center mb-2 md:mb-0">
              {isEnableMeterFilter ? (
                <button
                  onClick={() =>
                    handleMeterFilterItem({
                      ...meterFilter,
                      yes: !meterFilter.yes,
                    })
                  }
                >
                  <img
                    className="min-w-[14px] max-w-[14px] mr-2"
                    alt="checked"
                    src={
                      meterFilter.yes
                        ? "/icons/checked.svg"
                        : "/icons/unchecked.svg"
                    }
                  />
                </button>
              ) : (
                <img
                  className="min-w-[14px] max-w-[14px] mr-2"
                  alt="Percent of Yes answers"
                  src="/icons/YES.svg"
                />
              )}
              {meterLabels.YES} - {data?.yesNoAnswerPercents.YES || 0}%
            </p>
            <div
              className={`bar h-[0.65rem] flex-grow bg-[#F1F4F6] md:bg-gray-200 rounded-sm ${
                isEnableMeterFilter && !meterFilter.yes ? "bg-opacity-50" : ""
              }`}
            >
              <div
                style={{
                  width: `${data?.yesNoAnswerPercents.YES || 0}%`,
                }}
                className={`${
                  isEnableMeterFilter && !meterFilter.yes
                    ? "bg-[#688092] bg-opacity-50"
                    : "bg-[#46A759]"
                } h-full rounded`}
              ></div>
            </div>
          </div>
          <div className="md:flex items-center">
            <p className="w-[129px] flex items-center mb-2 md:mb-0">
              {isEnableMeterFilter ? (
                <button
                  onClick={() =>
                    handleMeterFilterItem({
                      ...meterFilter,
                      possibly: !meterFilter.possibly,
                    })
                  }
                >
                  <img
                    className="min-w-[14px] max-w-[14px] mr-2"
                    alt="checked"
                    src={
                      meterFilter.possibly
                        ? "/icons/checked.svg"
                        : "/icons/unchecked.svg"
                    }
                  />
                </button>
              ) : (
                <img
                  className="min-w-[14px] max-w-[14px] mr-2"
                  alt="Percent of Possibly answers"
                  src="/icons/POSSIBLY.svg"
                />
              )}
              {meterLabels.POSSIBLY} - {data?.yesNoAnswerPercents.POSSIBLY || 0}
              %
            </p>
            <div
              className={`bar h-[0.65rem] flex-grow bg-[#F1F4F6] md:bg-gray-200 rounded-sm ${
                isEnableMeterFilter && !meterFilter.possibly
                  ? "bg-opacity-50"
                  : ""
              }`}
            >
              <div
                style={{
                  width: `${data?.yesNoAnswerPercents.POSSIBLY || 0}%`,
                }}
                className={`${
                  isEnableMeterFilter && !meterFilter.possibly
                    ? "bg-[#688092] bg-opacity-50"
                    : "bg-[#FFB800]"
                } w-[10%] h-full rounded`}
              ></div>
            </div>
          </div>
          <div className="md:flex items-center">
            <p className="w-[129px] flex items-center mb-2 md:mb-0">
              {isEnableMeterFilter ? (
                <button
                  onClick={() =>
                    handleMeterFilterItem({
                      ...meterFilter,
                      no: !meterFilter.no,
                    })
                  }
                >
                  <img
                    className="min-w-[14px] max-w-[14px] mr-2"
                    alt="checked"
                    src={
                      meterFilter.no
                        ? "/icons/checked.svg"
                        : "/icons/unchecked.svg"
                    }
                  />
                </button>
              ) : (
                <img
                  className="min-w-[14px] max-w-[14px] mr-2"
                  alt="Percent of No answers"
                  src="/icons/NO.svg"
                />
              )}
              {meterLabels.NO} - {data?.yesNoAnswerPercents.NO || 0}%
            </p>
            <div
              className={`bar h-[0.65rem] flex-grow bg-[#F1F4F6] md:bg-gray-200 rounded-sm ${
                isEnableMeterFilter && !meterFilter.no ? "bg-opacity-50" : ""
              }`}
            >
              <div
                style={{ width: `${data?.yesNoAnswerPercents.NO || 0}%` }}
                className={`${
                  isEnableMeterFilter && !meterFilter.no
                    ? "bg-[#688092] bg-opacity-50"
                    : "bg-[#E3504F]"
                } w-[5%] h-full rounded`}
              ></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default YesNoMeter;
