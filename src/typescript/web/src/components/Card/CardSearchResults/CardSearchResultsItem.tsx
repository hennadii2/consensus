import classNames from "classnames";
import BookmarkButton from "components/Button/BookmarkButton/BookmarkButton";
import Card from "components/Card";
import ResultDetailItemExtras from "components/ResultDetailItem";
import StudySnapshot from "components/StudySnapshot/StudySnapshot";
import EnhancedTag from "components/Tag/EnhancedTag";
import MeterTag from "components/Tag/MeterTag";
import Tooltip from "components/Tooltip";
import CreateBookmarkItemTooltip from "components/Tooltip/CreateBookmarkItemTooltip/CreateBookmarkItemTooltip";
import VerticalDivider from "components/VerticalDivider";
import { FeatureFlag } from "enums/feature-flag";
import { Badges, ISearchItem } from "helpers/api";
import { IBookmarkItem, isPaperBookMarked } from "helpers/bookmark";
import { detailPagePath } from "helpers/pageUrl";
import useIsFeatureEnabled from "hooks/useIsFeatureEnabled";
import { useAppSelector } from "hooks/useStore";
import Link from "next/link";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { YesNoType } from "types/YesNoType";

type CardSearchResultsItemProps = {
  item: ISearchItem;
  onClickShare?: (item: ISearchItem, index: number) => void;
  onClickItem?: (item: ISearchItem, index: number) => void;
  onClickCite?: (item: ISearchItem, index: number) => void;
  onClickSave?: (item: ISearchItem, index: number) => void;
  index: number;
  meter?: YesNoType;
  isLoadingStudyType?: boolean;
};

/**
 * @component CardSearchResultsItem
 * @description Component for result item
 * @example
 * return (
 *   <CardSearchResultsItem item={{ ...args }} />
 * )
 */
const CardSearchResultsItem = ({
  item,
  index,
  onClickShare,
  onClickItem,
  onClickCite,
  onClickSave,
  meter,
  isLoadingStudyType,
}: CardSearchResultsItemProps) => {
  const { url_slug, id, paper_id, text, title, badges } = item;
  const isLimitedBookmarkItem = useAppSelector(
    (state) => state.bookmark.isLimitedBookmarkItem
  );
  const enhanced = badges ? Boolean(badges.enhanced) : false;
  const [tooltipInstance, setTooltipInstance] = useState<any>(null);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const bookmarkItems: { [key: number]: IBookmarkItem[] } = useAppSelector(
    (state) => state.bookmark.bookmarkItems
  );

  const features = {
    bookmark: useIsFeatureEnabled(FeatureFlag.BOOKMARK),
    studySnapShot: useIsFeatureEnabled(FeatureFlag.STUDY_SNAPSHOT),
    enablePaperSearch: useIsFeatureEnabled(FeatureFlag.PAPER_SEARCH),
  };

  // TODO(jlongley): Fix temporary workaround for identifying paper links when
  // this component is reused from the bookmarks view.
  const isPaperItem = id === paper_id;
  const link = detailPagePath(
    url_slug,
    id,
    features.enablePaperSearch || isPaperItem
  );

  useEffect(() => {
    setIsBookmarked(isPaperBookMarked(paper_id, bookmarkItems));
  }, [setIsBookmarked, bookmarkItems, id, paper_id]);

  const handleHideTooltip = useCallback(async () => {
    if (tooltipInstance != null) {
      tooltipInstance?.hide();
    }
  }, [tooltipInstance]);

  const hasBadges = useMemo(() => {
    let _hasBadges = false;
    Object.keys(item.badges).forEach((itemBadge) => {
      const badge = item.badges[itemBadge as keyof Badges];
      if (typeof badge === "boolean" && badge === true) {
        _hasBadges = true;
      }
      if (typeof badge === "object" && badge) {
        if (
          (badge as Badges["disputed"])?.reason &&
          (badge as Badges["disputed"])?.url
        ) {
          _hasBadges = true;
        } else {
          Object.keys(badge).forEach((subItemBadge) => {
            const subBadge = badge[subItemBadge as keyof Badges["study_type"]];
            if (typeof subBadge === "boolean" && subBadge === true) {
              _hasBadges = true;
            }
          });
        }
      }
    });
    return _hasBadges;
  }, [item.badges]);

  return (
    <div data-testid="card-search-result-item" className="relative">
      <Card key={id} className="hover:shadow-lg pb-[26px]">
        <span style={{ display: "none" }} className="zotero-doi">
          DOI: {item.doi}
        </span>
        <Link href={link} legacyBehavior>
          <a
            data-testid="result-item-link"
            onClick={(e) => {
              const target = e.target;
              if (
                target instanceof HTMLElement &&
                (target.id === "enhanced-indicator-element" ||
                  target.id === "tippy-backdrop")
              ) {
                e.preventDefault();
              } else {
                onClickItem?.(item, index);
              }
            }}
            data-test-text={link}
          >
            <div className="flex flex-col items-start sm:text-center justify-between sm:flex-row mb-3">
              <div className=" flex-nowrap flex mb-2.5 sm:mb-0 items-start justify-start">
                <img
                  className="w-3.5 mr-2 mt-[1px]"
                  src="/icons/document.svg"
                  alt="document"
                />
                <p
                  className={`text-[#222F2B] text-left text-base content line-clamp-2 font-bold leading-[18px] ${
                    !hasBadges ? "md:mr-[260px]" : ""
                  }`}
                >
                  {title}
                </p>
              </div>
              <div className="flex items-start justify-between order-1 w-full sm:w-auto">
                <div className={`flex flex-row space-x-3`}>
                  <EnhancedTag enhanced={enhanced} />
                  {meter ? <MeterTag meter={meter} /> : null}
                </div>
              </div>
            </div>
            <div className="mb-3">
              <h2
                className="order-2 text-base sm:text-lg result-text-content sm:order-1 sm:leading-8 text-[#364B44] bg-[#F1F4F6] p-4 rounded-2xl"
                dangerouslySetInnerHTML={{ __html: text }}
              />
            </div>
            <div className="flex items-end justify-between mt-[6px] md:mt-2">
              <ResultDetailItemExtras
                journal={item.journal}
                year={item.year}
                primary_author={item.primary_author}
                badges={item.badges}
                id={item.id}
                isLoadingStudyType={isLoadingStudyType}
                citation_count={item.citation_count}
              />
              <div className="w-6" />
            </div>
          </a>
        </Link>

        <div className="w-full h-[1px] bg-gray-200 mt-[16px] mb-[16px]"></div>

        <div className={classNames("flex justify-between md:relative")}>
          <div className="flex md:hidden items-center justify-end space-x-4 w-full pr-[26px] absolute bottom-[-10px] md:bottom-[-18px] right-0">
            {features.bookmark && (
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
                  <CreateBookmarkItemTooltip onClick={handleHideTooltip} />
                }
                className="ml-5 rounded-xl premium-bookmark-popup"
                disabled={isLimitedBookmarkItem !== true || isBookmarked}
              >
                <BookmarkButton
                  isBookmarked={isBookmarked}
                  isMobile={true}
                  onClick={() => {
                    if (isLimitedBookmarkItem === false || isBookmarked) {
                      onClickSave?.(item, index);
                    }
                  }}
                />
              </Tooltip>
            )}

            {!features.bookmark ? (
              <button
                onClick={() => onClickCite?.(item, index)}
                className="flex justify-center bg-white h-10 w-10 rounded-full items-center cursor-pointer shadow-[0_4px_20px_rgba(189,201,219,0.26)] backdrop-blur"
              >
                <img
                  alt="cite"
                  src="/icons/quotation-mark.svg"
                  className="w-5 h-5"
                />
              </button>
            ) : null}

            <button
              onClick={() => onClickShare?.(item, index)}
              className="flex justify-center bg-white h-10 w-10 rounded-full items-center cursor-pointer shadow-[0_4px_20px_rgba(189,201,219,0.26)] backdrop-blur"
            >
              <img alt="share" src="/icons/share.svg" className="w-5 h-5" />
            </button>
          </div>
          <div
            className={classNames(
              "hidden md:flex flex-1 items-center space-x-1 justify-end mt-[0px]",
              features.studySnapShot
                ? "absolute bottom-[-29px] right-0"
                : "relative"
            )}
          >
            {features.bookmark && (
              <>
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
                    <CreateBookmarkItemTooltip onClick={handleHideTooltip} />
                  }
                  className="ml-5 rounded-xl premium-bookmark-popup"
                  disabled={isLimitedBookmarkItem !== true || isBookmarked}
                >
                  <BookmarkButton
                    isBookmarked={isBookmarked}
                    isMobile={false}
                    onClick={() => {
                      if (isLimitedBookmarkItem === false || isBookmarked) {
                        onClickSave?.(item, index);
                      }
                    }}
                  />
                </Tooltip>

                <VerticalDivider />
              </>
            )}

            <button
              className="flex items-center font-bold text-sm space-x-2 text-black hover:bg-gray-100 rounded-lg px-2 py-[6px]"
              onClick={() => onClickCite?.(item, index)}
            >
              <img
                alt="cite"
                src="/icons/quotation-mark.svg"
                className="w-5 h-5 mr-2"
              />
              Cite
            </button>
            <VerticalDivider />

            <button
              className="flex items-center font-bold text-sm space-x-2 text-black hover:bg-gray-100 rounded-lg px-2 py-[6px]"
              onClick={() => onClickShare?.(item, index)}
            >
              <img
                alt="share"
                src="/icons/share.svg"
                className="w-5 h-5 mr-2"
              />
              Share
            </button>
          </div>
        </div>

        {features.studySnapShot && (
          <StudySnapshot
            paperId={paper_id}
            isDetailPage={false}
            badges={item?.badges}
          />
        )}
      </Card>
    </div>
  );
};

export default CardSearchResultsItem;
