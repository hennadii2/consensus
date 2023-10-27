import useLabels from "hooks/useLabels";

export default function FindingMissing() {
  const [pageLabels] = useLabels("screens.findingmissing");

  return (
    <div
      data-testid="findingmissing"
      className="container max-w-6xl m-auto grid grid-cols-1 md:grid-cols-2 pt-4 md:pt-16"
    >
      <div>
        <div className="block md:hidden mx-16 mt-6">
          <img alt="findingmissing" src="/images/findingmissing.svg" />
        </div>
        <h1 className="text-[27px] md:text-4xl leading-8 font-bold text-[#085394] mt-16 md:mt-24">
          {pageLabels["title"]}
        </h1>
        <p className="text-gray-900 mt-2 md:mt-16 max-w-[391px]">
          {pageLabels["description"]}
        </p>
      </div>
      <div className="hidden md:block">
        <img alt="findingmissing" src="/images/findingmissing.svg" />
      </div>
    </div>
  );
}
