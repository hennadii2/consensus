/* eslint-disable react/display-name */
import { CardSearchResultsItem } from "components/Card";
import LabelMoreResults from "components/LabelRelevantResults/LabelMoreResults";
import { ISearchItem } from "helpers/api";
import { debounce } from "lodash";
import isEqual from "lodash/isEqual";
import React, { useEffect } from "react";
import { YesNoType } from "types/YesNoType";

type CardSearchResultsProps = {
  items: ISearchItem[];
  onClickShare?: (item: ISearchItem, index: number) => void;
  onClickItem?: (item: ISearchItem, index: number) => void;
  onClickCite?: (item: ISearchItem, index: number) => void;
  onClickSave?: (item: ISearchItem, index: number) => void;
  resultIdToYesNoAnswer?: { [resultId: string]: YesNoType };
  isLoadingStudyType?: boolean;
  indexLabelMoreResults?: number;
};

/**
 * @component CardSearchResults
 * @description Container component for result items
 * @example
 * return (
 *   <CardSearchResults items={[...list]} />
 * )
 */
const CardSearchResults = React.memo(
  ({
    items,
    onClickShare,
    onClickItem,
    onClickCite,
    onClickSave,
    resultIdToYesNoAnswer,
    isLoadingStudyType,
    indexLabelMoreResults,
  }: CardSearchResultsProps) => {
    const zoteroItemUpdated = debounce(() => {
      // Force Zotero to refresh metadata - When the display is loaded (component did mount), trigger a ZoteroItemUpdated event to instruct Zotero to re-detect metadata on the page.
      // https://www.zotero.org/support/dev/exposing_metadata#force_zotero_to_refresh_metadata
      document.dispatchEvent(
        new Event("ZoteroItemUpdated", {
          bubbles: true,
          cancelable: true,
        })
      );
    }, 1000);

    useEffect(() => {
      if (items.length > 0) {
        const doiElement = document.getElementsByClassName("zotero-doi");
        if (doiElement.length > 0) {
          zoteroItemUpdated();
        }
      }
    }, [items, zoteroItemUpdated]);

    return (
      <div
        className="flex flex-col mt-4 gap-y-5"
        data-testid="card-search-results"
      >
        {items.map((item, index) => (
          <div key={item.id + index}>
            {indexLabelMoreResults === index ? <LabelMoreResults /> : null}
            <CardSearchResultsItem
              onClickShare={onClickShare}
              onClickItem={onClickItem}
              onClickCite={onClickCite}
              onClickSave={onClickSave}
              index={index}
              item={item}
              meter={resultIdToYesNoAnswer?.[item.id]}
              isLoadingStudyType={
                item.badges
                  ? item.badges.study_type
                    ? false
                    : isLoadingStudyType
                  : isLoadingStudyType
              }
            />
          </div>
        ))}
      </div>
    );
  },
  isEqual
);

export default CardSearchResults;
