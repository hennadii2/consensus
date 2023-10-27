import { useAuth } from "@clerk/nextjs";
import Tooltip from "components/Tooltip";
import CreateBookmarkItemTooltip from "components/Tooltip/CreateBookmarkItemTooltip/CreateBookmarkItemTooltip";
import path from "constants/path";
import { useAppSelector } from "hooks/useStore";
import { useRouter } from "next/router";
import React, { ReactNode, useCallback, useState } from "react";

type Props = {
  children?: ReactNode;
  onClick?: () => void;
  dataTestId?: string;
  isBookmarked: boolean;
  className?: string;
  disabled?: boolean;
};

/**
 * @component SaveSearchButton
 * @description designed for save search button
 * @example
 * return (
 *   <SaveSearchButton onClick={fn}>Learn more</SaveSearchButton>
 * )
 */
const SaveSearchButton = ({
  children,
  onClick,
  dataTestId,
  isBookmarked,
  className,
  disabled,
}: Props) => {
  const router = useRouter();
  const { isSignedIn, isLoaded } = useAuth();
  const isLimitedBookmarkItem = useAppSelector(
    (state) => state.bookmark.isLimitedBookmarkItem
  );
  const [tooltipInstance, setTooltipInstance] = useState<any>(null);

  const handleClickSaveSearchButton = useCallback(async () => {
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

    if (isLimitedBookmarkItem === false && onClick) {
      onClick();
    }
  }, [router, isSignedIn, isLoaded, isLimitedBookmarkItem, onClick]);

  return (
    <Tooltip
      interactive
      maxWidth={340}
      onShown={(instance: any) => {
        setTooltipInstance(instance);
      }}
      onHidden={(instance: any) => {
        setTooltipInstance(instance);
      }}
      tooltipContent={
        <CreateBookmarkItemTooltip
          onClick={() => {
            if (tooltipInstance != null) {
              tooltipInstance?.hide();
            }
          }}
        />
      }
      className="rounded-xl mt-2 ml-5 premium-bookmark-popup"
      disabled={isLimitedBookmarkItem !== true}
    >
      <button
        onClick={() => {
          handleClickSaveSearchButton();
        }}
        disabled={disabled}
        data-testid={dataTestId}
        className={`relative text-base bg-white text-[#222F2B] border border-[#DEE0E3] flex items-center justify-center w-[44px] h-[44px] md:w-[auto] md:gap-x-2 px-0 md:px-[14px] rounded-full hover:shadow-[0_2px_4px_0_rgba(189,201,219,0.32)] ${className}`}
      >
        {isBookmarked ? (
          <img
            alt="bookmark"
            src="/icons/bookmark-green.svg"
            className="w-[18px] h-[18px]"
          />
        ) : (
          <img
            alt="bookmark"
            src="/icons/bookmark-outline.svg"
            className="w-[18px] h-[18px]"
          />
        )}
        <span className="hidden md:block whitespace-nowrap">
          {isBookmarked ? "Saved search" : "Save search"}
        </span>
        {children}
      </button>
    </Tooltip>
  );
};

export default SaveSearchButton;
