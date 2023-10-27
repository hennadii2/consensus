import useLabels from "hooks/useLabels";

type Props = {
  numRelevantResults?: number;
  numTopResults?: number;
  isEnd?: boolean;
};

const LabelRelevantResults = ({
  numRelevantResults = 0,
  numTopResults = 0,
  isEnd = false,
}: Props) => {
  const [pageLabels] = useLabels("screens.search");

  if (
    numRelevantResults > 0 &&
    numRelevantResults === numTopResults &&
    !isEnd
  ) {
    return (
      <div className="flex-1 mt-5">
        <span className="leading-6 text-[#688092]">{`${numTopResults}+ ${pageLabels["relevant-results"]}`}</span>
      </div>
    );
  }

  if (numRelevantResults > 0) {
    return (
      <div className="flex-1 mt-5">
        <span className="leading-6 text-[#688092]">{`${numRelevantResults} ${pageLabels["relevant-results"]}`}</span>
      </div>
    );
  }

  return (
    <div className="flex-1 mt-5">
      <div className="flex flex-row space-x-4 mb-[23px]">
        <div className="w-10 h-10 min-w-[40px] sm:w-[54px] sm:min-w-[54px] sm:h-[54px] rounded-xl bg-white flex items-center justify-center">
          <img
            alt="search"
            className="w-6 h-6 sm:w-8 sm:h-8"
            src="/icons/search_relevant.svg"
          />
        </div>
        <div className="flex flex-col justify-around sm:justify-between">
          <span className="text-base md:text-lg text-[#222F2B] font-bold leading-[24px] md:leading-[27px]">
            We didn't find many highly relevant results for your search
          </span>
          <span className="text-[#688092] text-sm md:text-base leading-[21px] md:leading-6 mt-[6px]">
            Need help getting better results? Visit our{" "}
            <a
              href="https://consensus.app/home/blog/maximize-your-consensus-experience-with-these-best-practices/"
              className="text-[#2AA3EF] font-bold"
            >
              how to search
            </a>{" "}
            page
          </span>
        </div>
      </div>
      <span className="text-sm md:text-base leading-6 text-[#688092]">
        {pageLabels["most-relevant-results"]}:
      </span>
    </div>
  );
};

export default LabelRelevantResults;
