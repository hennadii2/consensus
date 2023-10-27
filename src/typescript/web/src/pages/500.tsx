import Head from "components/Head";
import useLabels from "hooks/useLabels";

export default function ServerError() {
  const [pageLabels] = useLabels("screens.servererror");

  return (
    <>
      <Head title={pageLabels["title"]} />
      <div className="container max-w-6xl m-auto grid grid-cols-1 md:grid-cols-2 pt-4 md:pt-16 text-center md:text-left mb-20">
        <div>
          <h1 className="text-7xl font-bold text-[#085394] mt-6 md:mt-24">
            500
          </h1>
          <div className="block md:hidden mx-16 mt-6">
            <img alt="servererror" src="/images/servererror.svg" />
          </div>
          <h1 className="text-[27px] md:text-4xl leading-8 font-bold text-[#085394] mt-6 md:mt-2">
            {pageLabels["oops"]}
          </h1>
          <p className="text-gray-900 mt-2 md:mt-16 max-w-[391px]">
            {pageLabels["description"]}
          </p>
        </div>
        <div className="flex justify-center hidden md:block">
          <img alt="servererror" src="/images/servererror.svg" />
        </div>
      </div>
    </>
  );
}
