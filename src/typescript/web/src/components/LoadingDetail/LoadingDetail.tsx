import Icon from "components/Icon";
import VerticalDivider from "components/VerticalDivider";
import useLabels from "hooks/useLabels";

export const BadgesLoading = () => {
  return (
    <>
      <div className="mr-4 w-full h-[1px] bg-[#DEE0E3] sm:-mx-2 mt-10 block md:hidden" />
      <div className="flex justify-between mt-4 md:mt-6 items-center sm:-mx-2">
        <div className="flex items-center flex-wrap w-full">
          <div className="mr-4 mb-2 md:mb-0 bg-[#F1F4F6] h-3 w-full sm:w-full md:w-[300px] rounded-xl" />
          <div className="mr-4 mb-3 sm:mb-0 w-[1px] h-[17px] bg-[#DEE0E3] hidden md:block" />
          <div className="mr-4 bg-[#F1F4F6] h-3 w-20 xs:w-[104px] rounded-xl" />
          <div className="mr-4 w-[1px] h-[17px] bg-[#DEE0E3]" />
          <div className="mr-4 bg-[#F1F4F6] h-3 w-[37px] rounded-xl" />
          <div className="space-x-2 items-center rounded-md flex md:hidden">
            <div className="bg-loading-200 h-3 w-10 sm:w-[100px] rounded-xl" />
            <div className="bg-loading-200 h-3 w-3 rounded-xl" />
          </div>
        </div>
        <div className="space-x-2 items-center rounded-md hidden md:flex">
          <div className="bg-loading-200 h-3 w-[100px] rounded-xl" />
          <div className="bg-loading-200 h-3 w-3 rounded-xl" />
        </div>
      </div>
    </>
  );
};

export default function LoadingDetail() {
  const [pageLabels] = useLabels("screens.details");
  const [studySnapshotLabel] = useLabels("study-snapshot");

  return (
    <div
      data-testid="loadingdetail"
      className="flex justify-between bg-white rounded-2xl flex-nowrap detail-content"
    >
      <div
        data-testid="result-paper"
        className="animate-pulse w-full detail-left-panel pt-5 lg:pt-8 lg:pb-8 px-5 lg:px-8 lg:border-r border-r-gray-200"
      >
        <div className="bg-loading-200 h-4 w-full  rounded-xl mb-1.5" />
        <div className="bg-loading-200 h-4 w-[95%] rounded-xl" />

        <div className="flex flex-row items-center gap-x-2 mt-3">
          <Icon
            size={16}
            className="text-gray-550 w-4 min-w-[16px]"
            name="users"
          />
          <div className="bg-[#F1F4F6] h-3 w-full  rounded-xl" />
        </div>
        <div className="flex flex-row items-center gap-x-2 mt-[8px]">
          <Icon
            size={16}
            className="text-gray-550 w-4 min-w-[16px]"
            name="calendar"
          />
          <div className="bg-[#F1F4F6] h-3 w-[36px]  rounded-xl" />
        </div>

        <div className="flex justify-start items-center space-x-3 mt-[18px]">
          <div className="flex items-center">
            <img
              alt="bookmark"
              src="/icons/bookmark-outline-blue.svg"
              className="w-5 h-5 mr-2"
            />
            <div className="bg-loading-200 h-4 w-[35px]  rounded-xl" />
          </div>
          <VerticalDivider />
          <div className="flex items-center">
            <img
              alt="bookmark"
              src="/icons/quotation-mark.svg"
              className="w-5 h-5 mr-2"
            />
            <div className="bg-loading-200 h-4 w-[35px]  rounded-xl" />
          </div>
          <VerticalDivider />
          <div className="flex items-center">
            <img
              alt="bookmark"
              src="/icons/share.svg"
              className="w-5 h-5 mr-2"
            />
            <div className="bg-loading-200 h-4 w-[35px]  rounded-xl" />
          </div>
        </div>
        <div className="w-full h-[1px] bg-gray-200 my-[20px]" />

        <div
          data-testid="result-detail-extras"
          className="flex flex-col items-start sm:gap-y-5 gap-y-[26px]"
        >
          <div className="flex flex-col items-start sm:flex-row sm:gap-y-0 gap-y-3 w-full">
            <div className="min-w-[136px]">
              <p className="text-sm text-[#808993]">
                {pageLabels["citations"]}
              </p>
            </div>
            <div className="flex-1 w-full">
              <div className="flex items-center">
                <div className="bg-loading-200 h-4 w-[80%]  rounded-xl" />
                <img
                  alt="bookmark"
                  src="/icons/info.svg"
                  className="w-5 h-5 ml-1"
                />
              </div>
              <div className="bg-loading-200 h-4 w-[35px] rounded-xl mt-1.5 hidden sm:block" />
            </div>
          </div>
          <div className="flex-col items-start hidden sm:flex sm:items-center sm:flex-row sm:gap-y-0 gap-y-3 w-full">
            <div className="min-w-[136px]">
              <p className="text-sm text-[#808993]">
                {pageLabels["quality-indicators"]}
              </p>
            </div>
            <div className="flex-1">
              <div className="bg-[#F1F4F6] h-8 w-[132px]  rounded-md" />
            </div>
          </div>
        </div>

        <div className="my-[26px]">
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
          <div className="px-5 pb-5 pt-4 bg-[#F1F4F6] rounded-b-2xl flex flex-col gap-y-4 relative">
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
              <div className="flex-1 gap-1.5 flex flex-col w-full">
                <div className="bg-loading-200 h-3 w-[100%]  rounded-sm" />
                <div className="bg-loading-200 h-3 w-[100%]  rounded-sm" />
              </div>
            </div>

            <div className="flex flex-col items-start sm:items-center justify-start sm:flex-row sm:gap-x-1 sm:gap-y-0 gap-y-1">
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
              <div className="flex-1 gap-1.5 flex flex-col">
                <div className="bg-loading-200 h-3 w-[46px]  rounded-sm" />
              </div>
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
              <div className="flex-1 gap-1.5 flex flex-col w-full">
                <div className="bg-loading-200 h-3 w-[100%]  rounded-sm" />
                <div className="bg-loading-200 h-3 w-[100%]  rounded-sm" />
              </div>
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
              <div className="flex-1 gap-1.5 flex flex-col w-full">
                <div className="bg-loading-200 h-3 w-[100%]  rounded-sm" />
                <div className="bg-loading-200 h-3 w-[100%]  rounded-sm" />
                <div className="bg-loading-200 h-3 w-[100%]  rounded-sm" />
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-col items-start sm:flex-row sm:gap-y-0 gap-y-3 mt-6">
          <div className="min-w-[71px]">
            <p data-testid="result-journal" className="text-sm text-gray-500">
              {pageLabels["journal"]}
            </p>
          </div>
          <div className="flex flex-col gap-y-2 flex-1">
            <div className="bg-loading-200 h-3 w-[80%]  rounded-sm" />
            <div className="flex items-center gap-1">
              <div className="bg-[#F1F4F6] h-4 w-[78px]  rounded-xl" />
              <div className="bg-loading-200 h-2 w-[20px]  rounded-xl" />
              <div className="bg-loading-200 h-2 w-[20px]  rounded-xl" />
              <div className="bg-loading-200 h-2 w-[20px]  rounded-xl" />
              <div className="bg-loading-200 h-2 w-[20px]  rounded-xl" />
            </div>
          </div>
        </div>
      </div>

      <div className="w-full h-[1px] lg:hidden bg-gray-200 my-[26px]" />
      <div className="lg:flex-grow animate-pulse">
        <div className="w-full px-5 pb-5 lg:pb-8 lg:pt-8 lg:px-8">
          <div className="flex flex-row items-center gap-x-4">
            <div className="flex items-center">
              <img
                className="w-5 h-5 mr-2"
                alt="Open in new"
                src="/icons/open-in-new.svg"
              />
              <div className="bg-loading-200 h-4 w-[35px]  rounded-xl" />
            </div>
            <div className="flex items-center">
              <img
                className="w-5 h-5 mr-2"
                alt="Semantic Scholar"
                src="/icons/semantic-scholar.svg"
              />
              <div className="bg-loading-200 h-4 w-[35px]  rounded-xl" />
            </div>
            <div className="flex items-center">
              <img className="w-5 h-5 mr-2" alt="PDF" src="/icons/pdf.svg" />
              <div className="bg-loading-200 h-4 w-[35px]  rounded-xl" />
            </div>
          </div>

          <div
            data-testid="result-claim"
            className="rounded-xl p-5 bg-[#F1F4F6] my-5 sm:my-[26px] flex"
          >
            <img
              className="min-w-[24px] max-w-[24px] h-6 w-6 mr-[6px]"
              alt="Sparkler"
              src="/icons/sparkler.svg"
            />
            <div className="flex-1 gap-1.5 flex flex-col">
              <div className="bg-loading-200 h-3 w-[95%]  rounded-sm" />
              <div className="bg-loading-200 h-3 w-[100%]  rounded-sm" />
              <div className="bg-loading-200 h-3 w-[93%]  rounded-sm" />
              <div className="bg-loading-200 h-3 w-[95%]  rounded-sm" />
            </div>
          </div>
          <div>
            <p className="mb-2 text-sm text-gray-500">
              {pageLabels["abstract"]}
            </p>
            <div className="gap-2 flex flex-col">
              <div className="bg-loading-200 h-3 w-[95%]  rounded-sm" />
              <div className="bg-loading-200 h-3 w-[100%]  rounded-sm" />
              <div className="bg-loading-200 h-3 w-[93%]  rounded-sm" />
              <div className="bg-loading-200 h-3 w-[98%]  rounded-sm" />

              <div className="bg-loading-200 h-3 w-[95%]  rounded-sm" />
              <div className="bg-loading-200 h-3 w-[95%]  rounded-sm" />
              <div className="bg-loading-200 h-3 w-[98%]  rounded-sm" />
              <div className="bg-loading-200 h-3 w-[95%]  rounded-sm" />

              <div className="bg-loading-200 h-3 w-[95%]  rounded-sm" />
              <div className="bg-loading-200 h-3 w-[98%]  rounded-sm" />
              <div className="bg-loading-200 h-3 w-[95%]  rounded-sm" />
              <div className="bg-loading-200 h-3 w-[93%]  rounded-sm" />

              <div className="bg-loading-200 h-3 w-[98%]  rounded-sm" />
              <div className="bg-loading-200 h-3 w-[95%]  rounded-sm" />
              <div className="bg-loading-200 h-3 w-[93%]  rounded-sm" />
              <div className="bg-loading-200 h-3 w-[95%]  rounded-sm" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
