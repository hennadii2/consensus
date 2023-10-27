import classNames from "classnames";
import {
  BOOKMARK_MAX_CUSTOM_LIST_NUM,
  BOOKMARK_MAX_ITEM_NUM,
} from "constants/config";
import { getBookmarkItemsCount } from "helpers/bookmark";
import {
  getReversedSubscriptionUsageData,
  ISubscriptionUsageData,
} from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React, { ReactNode } from "react";
import LoadingSubscriptionCard from "../LoadingSubscriptionCard/LoadingSubscriptionCard";

type Props = {
  children?: ReactNode;
  subscriptionUsageData: ISubscriptionUsageData;
  isPremium: boolean;
  className?: string;
  isLoading?: boolean;
};

/**
 * @component SubscriptionUsageCard
 * @description designed for subscription usage card
 * @example
 * return (
 *   <SubscriptionUsageCard>Learn more</SubscriptionUsageCard>
 * )
 */
const SubscriptionUsageCard = ({
  children,
  subscriptionUsageData,
  isPremium,
  className,
  isLoading,
}: Props) => {
  const subscription = useAppSelector(
    (state) => state.subscription.subscription
  );
  const [subscriptionUsageLabels] = useLabels("subscription-usage");
  const reversedSubscriptionUsageData = getReversedSubscriptionUsageData(
    subscriptionUsageData
  );
  const bookmarkLists = useAppSelector((state) => state.bookmark.bookmarkLists);
  const bookmarkItems = useAppSelector((state) => state.bookmark.bookmarkItems);
  const bookmarkItemNum = getBookmarkItemsCount(bookmarkItems);
  let bookmarkListLeft =
    BOOKMARK_MAX_CUSTOM_LIST_NUM - bookmarkLists.length + 1;
  let bookmarkItemsLeft = BOOKMARK_MAX_ITEM_NUM - bookmarkItemNum;
  if (bookmarkListLeft < 0) bookmarkListLeft = 0;
  if (bookmarkItemsLeft < 0) bookmarkItemsLeft = 0;

  if (isLoading) {
    return <LoadingSubscriptionCard />;
  }

  return (
    <>
      <h4 className="text-[#222F2B] font-bold text-lg">
        {subscriptionUsageLabels["title"]}
      </h4>

      <div
        className={classNames(
          "mt-6",
          isPremium ? "bg-[#F1F4F6] rounded-[12px] p-5" : ""
        )}
      >
        <div
          data-testid="subscription-usage-card-summaries-left"
          className="flex flex-wrap pl-1.5 items-center"
        >
          {isPremium && (
            <>
              <div className="w-full sm:w-[100%] md:w-[100%] flex flex-wrap items-baseline md:items-center">
                <div className="inline-block w-[6px] h-[6px] rounded-full bg-[#364B44]"></div>

                <div className="flex-1 ml-3.5 text-[#364B44] text-sm lg:text-base items-center flex flex-wrap flex-1">
                  <span
                    data-testid="ai-credits-unlimited-title"
                    className="mr-1"
                  >
                    {subscriptionUsageLabels["ai-credits"]}
                    <span className="ml-1 hidden md:inline-block">-</span>
                  </span>

                  <span className="font-bold w-full md:w-[auto]">
                    {subscriptionUsageLabels["unlimited"]}
                    <img
                      className="inline-block ml-1.5"
                      alt="Info"
                      src="/icons/endless.svg"
                    />
                  </span>
                </div>
              </div>

              <div className="w-full sm:w-[100%] md:w-[100%] flex flex-wrap items-baseline md:items-center mt-[20px]">
                <div className="inline-block w-[6px] h-[6px] rounded-full bg-[#364B44]"></div>

                <div className="flex-1 ml-3.5 text-[#364B44] text-sm lg:text-base items-center flex flex-wrap flex-1">
                  <span
                    data-testid="lists-bookmarks-unlimited-title"
                    className="mr-1"
                  >
                    {subscriptionUsageLabels["lists-bookmarks"]}
                    <span className="ml-1 hidden md:inline-block">-</span>
                  </span>

                  <span className="font-bold w-full md:w-[auto]">
                    {subscriptionUsageLabels["unlimited"]}
                    <img
                      className="inline-block ml-1.5"
                      alt="Info"
                      src="/icons/endless.svg"
                    />
                  </span>
                </div>
              </div>
            </>
          )}

          {!isPremium && (
            <>
              <div className="w-full flex items-center gap-x-[12px]">
                <div className="inline-block p-[12px] rounded-full bg-[#E4F2ED]">
                  <img
                    className="w-[20px] h-[20px]"
                    alt="coin"
                    src="/icons/coin-blue.svg"
                  />
                </div>

                <div className="flex-1 text-[#364B44] items-center flex flex-wrap">
                  <span
                    data-testid="no-credits-left-title"
                    className="w-full text-lg text-[#222F2B]"
                  >
                    {subscriptionUsageLabels["credit-left"].replace(
                      "{count}",
                      reversedSubscriptionUsageData.creditLeft
                    )}
                  </span>

                  <span
                    data-testid="refresh-date-text"
                    className="w-full text-[#688092] text-sm"
                  >
                    {subscriptionUsageLabels["refreshed-on"].replace(
                      "{date}",
                      reversedSubscriptionUsageData.refreshDate
                    )}
                  </span>
                </div>
              </div>

              <div className="w-full mt-[24px] flex gap-x-[12px]">
                <div className="inline-block p-[12px] rounded-full bg-[#E4F2ED]">
                  <img
                    className="w-[20px] h-[20px]"
                    alt="coin"
                    src="/icons/bookmark-outline-thin.svg"
                  />
                </div>

                <div className="flex-1 text-[#364B44] items-center flex flex-wrap">
                  <span
                    data-testid="no-bookmark-left-title"
                    className="w-full text-lg text-[#222F2B]"
                  >
                    {subscriptionUsageLabels["bookmark-left"]
                      .replace("{list count}", bookmarkListLeft)
                      .replace("{bookmark count}", bookmarkItemsLeft)}
                  </span>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
};

export default SubscriptionUsageCard;
