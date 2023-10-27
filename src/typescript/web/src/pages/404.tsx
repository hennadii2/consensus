import useLabels from "hooks/useLabels";

export default function PageNotFound() {
  const [pageLabels] = useLabels("screens.notfound");

  return (
    <div className="container max-w-6xl m-auto grid grid-cols-1 md:grid-cols-2 pt-0 md:pt-16 mb-20">
      <div>
        <h1 className="text-7xl font-bold text-[#085394] mt-6 md:mt-24 text-center md:text-left">
          404
        </h1>
        <div className="block md:hidden mx-16 mt-6">
          <img alt="notfound" src="/images/notfound.svg" />
        </div>
        <h1 className="text-[27px] md:text-4xl font-bold text-[#085394] mt-2">
          {pageLabels["title"]}
        </h1>
        <p
          dangerouslySetInnerHTML={{ __html: pageLabels["description"] }}
          className="text-gray-900 mt-2 md:mt-16 max-w-[391px]"
        ></p>
      </div>
      <div className="flex justify-center hidden md:block">
        <img alt="notfound" src="/images/notfound.svg" />
      </div>
    </div>
  );
}
