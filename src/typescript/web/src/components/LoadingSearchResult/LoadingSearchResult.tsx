import Card from "components/Card";

const MeterTagLoading = () => (
  <div>
    <div className="space-x-2 flex bg-[#F1F4F6] p-2.5 rounded-full">
      <div className="bg-loading-200 h-1.5 w-1.5  rounded-xl" />
      <div className="bg-loading-200 h-1.5 w-[24px] rounded-xl" />
    </div>
  </div>
);

export const BadgesLoading = () => {
  return (
    <div className="flex justify-between mt-6 items-end">
      <div className="flex items-center flex-wrap">
        <div className="mr-4 mb-3 sm:mb-0 space-x-2 flex border border-[#DEE0E3] p-2 rounded-md">
          <div className="bg-loading-200 h-3 w-3  rounded-xl" />
          <div className="bg-loading-200 h-3 w-[100px] rounded-xl" />
        </div>
        <div className="mr-4 mb-3 sm:mb-0 w-[1px] h-[17px] bg-[#DEE0E3] hidden md:block" />
        <div className="mr-4 mb-3 sm:mb-0 bg-[#F1F4F6] h-3 w-[237px] md:w-[161px] rounded-xl" />
        <div className="mr-4 mb-3 sm:mb-0 w-[1px] h-[17px] bg-[#DEE0E3] hidden md:block" />
        <div className="mr-4 bg-[#F1F4F6] h-3 w-[104px] rounded-xl" />
        <div className="mr-4 w-[1px] h-[17px] bg-[#DEE0E3]" />
        <div className="mr-4 bg-[#F1F4F6] h-3 w-[37px] rounded-xl" />
      </div>
      <div className="bg-loading-200 h-6 w-6 min-w-[24px] min-h-[24px] rounded-md"></div>
    </div>
  );
};

export default function LoadingSearchResult() {
  return (
    <div data-testid="loadingsearchresult" className="">
      {[0, 1, 2, 3].map((item, index) => (
        <Card className="mt-4" key={index}>
          <div className="flex md:hidden mb-3">
            <MeterTagLoading />
          </div>
          <div className="animate-pulse">
            <div className="flex space-x-10">
              <div className="flex-1">
                <div className="bg-loading-200 h-3 w-full  rounded-xl mb-3" />
                <div className="bg-loading-200 h-3 w-[80%] rounded-xl mb-3" />
                <div className="bg-loading-200 h-3 w-[90%] rounded-xl" />
              </div>
              <div className="hidden md:block">
                <MeterTagLoading />
              </div>
            </div>
            <BadgesLoading />
          </div>
        </Card>
      ))}
    </div>
  );
}
