import { TRY_SEARCH_URL } from "constants/config";
import useLabels from "hooks/useLabels";
import Link from "next/link";
import React from "react";

function BookmarkEmpty() {
  const [pageLabels] = useLabels("screens.bookmark-list-detail.empty-state");

  return (
    <div className="mt-10 mb-10 md:mt-20 md:mb-20 text-center">
      <div
        className="inline-block ml-auto mr-auto rounded-[20px] px-[18px] py-[60px] max-w-full"
        style={{
          background: "rgba(255, 255, 255, 0.70)",
          boxShadow: "0px 4px 20px 0px rgba(189, 201, 219, 0.26)",
        }}
      >
        <img
          src={"/icons/search-gray.svg"}
          className="w-[80px] h-[80px] ml-auto mr-auto mb-6"
          alt="search icon"
        />
        <h2
          data-testid="title"
          className="text-lg text-black font-bold w-full text-center"
        >
          {pageLabels["title"]}
        </h2>
        <p
          data-testid="try-searching"
          className="text-base text-[#688092] w-full text-center mt-2"
        >
          {pageLabels["try-searching"]}
        </p>

        <Link passHref href={TRY_SEARCH_URL} legacyBehavior>
          <a
            data-testid="query-link"
            className="block mt-[16px] ml-auto mr-auto text-center text-black text-sm px-[16px] py-[6px] border border-[#E4E9EC] rounded-[22px]"
          >
            {pageLabels["query-text"]}
          </a>
        </Link>
      </div>
    </div>
  );
}

export default BookmarkEmpty;
