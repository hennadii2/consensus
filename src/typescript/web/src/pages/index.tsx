import { withServerSideAuth } from "@clerk/nextjs/ssr";
import classNames from "classnames";
import Button from "components/Button";
import Head from "components/Head";
import { IconText } from "components/Icon";
import Logo from "components/Logo";
import SearchInput from "components/SearchInput";
import { META_SEARCH_IMAGE, TWITTER, WEB_URL_BLOG } from "constants/config";
import { getIp, getTrending, handleRedirect, TrendingItem } from "helpers/api";
import { searchPageUrl } from "helpers/pageUrl";
import { show as showIntercom } from "helpers/services/intercom";
import { setSynthesizeOn } from "helpers/setSynthesizeOn";
import useLabels from "hooks/useLabels";
import useSearch from "hooks/useSearch";
import type { GetServerSidePropsContext, NextPage } from "next";
import { useRef } from "react";
import Slider from "react-slick";
import "slick-carousel/slick/slick-theme.css";
import "slick-carousel/slick/slick.css";

type IndexProps = {
  trendings: string[];
  questionTypes: TrendingItem[];
  topics: TrendingItem[];
};
/**
 * @page Home
 * @description Index/Search page. First page when the user access the page
 */
const Home: NextPage<IndexProps> = ({
  trendings,
  questionTypes,
  topics,
}: IndexProps) => {
  const [pageLabels] = useLabels("screens.index");
  const { handleSearch } = useSearch();
  const sliderRef = useRef<Slider>(null);

  const handleClickHelp = (url: string) => {
    if (url === "intercom") {
      showIntercom();
    } else if (url === "twitter") {
      window.open(TWITTER);
    } else if (url === "blog") {
      window.open(WEB_URL_BLOG);
    }
  };

  const handleClickItem = (value: string) => {
    setSynthesizeOn();
    handleSearch(value);
  };

  return (
    <>
      <Head
        title={pageLabels.title}
        description={pageLabels.description}
        type="website"
        url={searchPageUrl()}
        image={META_SEARCH_IMAGE}
      />
      <div className="container sm:px-10 lg:px-20 2xl:px-60 sm:pt-20 pt-4">
        <div className="flex items-center flex-col">
          <Logo size="large" />
          <p
            data-testid="subtitle"
            className="text-xl md:text-2xl pt-8 pb-10 text-center font-medium"
          >
            {pageLabels.subtitle}
          </p>
          <div className={classNames("w-full flex justify-center")}>
            <SearchInput trendings={trendings} />
          </div>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4" data-testid="product-details">
        <h1 className="text-2xl md:text-4xl text-center font-bold mb-6">
          {pageLabels.question.title}
        </h1>
        <p className="px-4 lg:px-40 text-center mb-10 md:mb-16 text-gray-600">
          {pageLabels.question.text}
        </p>
        <div className="flex justify-center flex-wrap gap-x-6 gap-y-6 ">
          {questionTypes.map((item) => (
            <div key={item.key} className="w-full sm:w-[48%] md:w-[31%]">
              <IconText
                icon={item.key}
                items={item.queries}
                title={item.title}
                align="center"
                onClickItem={handleClickItem}
              />
            </div>
          ))}
        </div>
      </div>
      {/* Topics section */}
      <div className="background-landing-white pt-[860px] -mt-[860px] md:pt-[200px] md:-mt-[180px] pb-20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="mt-20">
            <h1 className="text-2xl md:text-4xl text-center font-bold mb-6">
              {pageLabels.topics.title}
            </h1>
            <p className="px-4 lg:px-40 text-center mb-4 text-gray-600">
              {pageLabels.topics.text}
            </p>
          </div>
          <div className="mx-[-0.5rem]">
            <Slider
              ref={sliderRef}
              dots
              slidesToShow={3}
              slidesToScroll={3}
              autoplaySpeed={8000}
              autoplay={true}
              onSwipe={() => sliderRef.current?.slickPause()}
              arrows={false}
              appendDots={(dots) => (
                <div onClick={(e) => sliderRef.current?.slickPause()}>
                  {dots}
                </div>
              )}
              responsive={[
                {
                  breakpoint: 1024,
                  settings: {
                    slidesToShow: 3,
                    slidesToScroll: 3,
                  },
                },
                {
                  breakpoint: 800,
                  settings: {
                    slidesToShow: 2,
                    slidesToScroll: 2,
                  },
                },
                {
                  breakpoint: 600,
                  settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                  },
                },
              ]}
            >
              {topics?.map((item) => (
                <div key={item.key} className="px-3 py-3 h-full">
                  <IconText
                    icon={item.key}
                    items={item.queries}
                    title={item.title}
                    onClickItem={handleClickItem}
                  />
                </div>
              ))}
            </Slider>
          </div>
        </div>
      </div>

      {/* Help */}
      <div className="background-landing pt-10 sm:pt-32 pb-20 px-4">
        <div className="max-w-7xl mx-auto px-4 flex flex-wrap">
          <div className="w-[100%] md:w-[45%] flex flex-col items-center md:items-start mb-10">
            <h1 className="text-2xl md:text-4xl font-bold mt-10 sm:mt-32">
              {pageLabels.help.title}
            </h1>
            <h1 className="text-2xl md:text-4xl font-bold consensus-text mt-2 mb-8">
              Consensus
            </h1>
            <a href="/home/about-us/">
              <Button variant="secondary">{pageLabels.help.button}</Button>
            </a>
          </div>
          <div className="w-[100%] md:w-[55%]">
            {pageLabels.help.items.map((item: any) => (
              <div
                key={item.icon}
                className="p-8 bg-white shadow-card mb-4 rounded-3xl flex items-center justify-between flex-col md:flex-row"
              >
                <div className="flex items-center flex-col md:flex-row">
                  <div className="h-[80px] w-[80px] bg-[#ECF6FE] rounded-xl flex items-center justify-center m-auto">
                    <img
                      src={`/icons/search/${item.icon}.svg`}
                      alt={item.text}
                    />
                  </div>
                  <p className="text-xl font-bold mt-2 mb-5 md:mt-0 md:mb-0 md:ml-6">
                    {item.text}
                  </p>
                </div>
                <Button
                  onClick={() => handleClickHelp(item.url)}
                  variant="primary"
                >
                  {item.button}
                </Button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
};

export const getServerSideProps = withServerSideAuth(
  async (context: GetServerSidePropsContext) => {
    try {
      const authToken = await (context.req as any).auth.getToken();
      const ipAddress = await getIp(context.req);
      const data = await getTrending({
        authToken,
        ipAddress,
        headers: context.req.headers,
      });
      return {
        props: {
          trendings: data.queries,
          questionTypes: data.questionTypes,
          topics: data.topics,
        },
      };
    } catch (error) {
      return handleRedirect(error);
    }
  },
  { loadUser: true }
);

export default Home;
