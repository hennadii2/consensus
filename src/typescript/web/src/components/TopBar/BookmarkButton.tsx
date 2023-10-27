import path from "constants/path";
import Link from "next/link";
import React from "react";

function BookmarkButton() {
  return (
    <Link href={path.LISTS} passHref legacyBehavior>
      <a className="bg-[#57AC91] w-10 h-10 rounded-full flex items-center justify-center mr-3">
        <img
          alt="bookmark"
          src="/icons/bookmark.svg"
          className="w-[22px] h-[22px]"
        />
      </a>
    </Link>
  );
}

export default BookmarkButton;
