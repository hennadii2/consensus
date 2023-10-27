import useLabels from "hooks/useLabels";

export default function NoSearchResult() {
  const [pageLabels] = useLabels("screens.nosearchresult");

  return (
    <div
      data-testid="nosearchresult"
      className="container max-w-6xl m-auto grid grid-cols-1 md:grid-cols-2 pt-0 md:pt-16"
    >
      <div>
        <div className="block md:hidden mx-16 mt-6">
          <img alt="nosearchresult" src="/images/nosearchresult.svg" />
        </div>
        <h1 className="text-[27px] leading-8 md:text-4xl font-bold text-[#085394] mt-24">
          {pageLabels["first-title"]}
        </h1>
        <h1 className="text-[27px] md:text-4xl font-bold text-[#085394] mt-6 md:mt-12">
          {pageLabels["second-title"]}
        </h1>
        <p className="text-gray-900 mt-2 md:mt-16 max-w-[391px]">
          {pageLabels["description"]}
          <br />
          <a
            href="mailto:support@consensus.app"
            className="text-[#085394] font-bold"
          >
            support@consensus.app
          </a>
        </p>
      </div>
      <div className="hidden md:block">
        <img alt="nosearchresult" src="/images/nosearchresult.svg" />
      </div>
    </div>
  );
}
