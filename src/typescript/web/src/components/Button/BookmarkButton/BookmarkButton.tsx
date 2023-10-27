import { useAuth } from "@clerk/nextjs";
import classNames from "classnames";
import path from "constants/path";
import { useRouter } from "next/router";
import React, { ReactNode, useCallback } from "react";

type Props = {
  children?: ReactNode;
  isBookmarked: boolean;
  isMobile?: boolean;
  onClick?: () => void;
};

/**
 * @component BookmarkButton
 * @description designed for bookmark button
 * @example
 * return (
 *   <BookmarkButton onClick={fn}>Learn more</SaveSearchButton>
 * )
 */
const BookmarkButton = ({
  children,
  isBookmarked,
  isMobile,
  onClick,
}: Props) => {
  const router = useRouter();
  const { isSignedIn, isLoaded } = useAuth();

  const handleClickButton = useCallback(async () => {
    if (!isLoaded) {
      router?.push(path.INTERNAL_SERVER_ERROR);
      return;
    }

    if (!isSignedIn) {
      router.push(
        `${path.SIGN_UP}#/?redirect_url=${encodeURIComponent(
          `${router?.asPath}`
        )}`
      );
      return;
    }

    if (onClick) {
      onClick();
    }
  }, [router, isSignedIn, isLoaded, onClick]);

  return (
    <button
      className={classNames(
        isMobile
          ? "flex justify-center bg-white h-10 w-10 rounded-full items-center cursor-pointer shadow-[0_4px_20px_rgba(189,201,219,0.26)] backdrop-blur"
          : "flex items-center font-bold text-sm space-x-2 text-[#364B44] relative hover:bg-[#F1F4F6] rounded-lg px-2 py-[6px]"
      )}
      onClick={handleClickButton}
    >
      {isBookmarked ? (
        <>
          <img
            alt="bookmark"
            src="/icons/bookmark-blue.svg"
            className="w-5 h-5"
          />
          {isMobile == false && <span className="ml-2">Saved</span>}
        </>
      ) : (
        <>
          <img
            alt="bookmark"
            src="/icons/bookmark-outline-blue.svg"
            className="w-5 h-5"
          />
          {isMobile == false && <span className="ml-2">Save</span>}
        </>
      )}
    </button>
  );
};

export default BookmarkButton;
