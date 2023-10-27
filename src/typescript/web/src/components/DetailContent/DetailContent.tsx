import Icon from "components/Icon";
import ResultDetailItemExtras from "components/ResultDetailItem";
import ResultDetailDoi from "components/ResultDetailItem/ResultDetailDoi";
import StudySnapshotDetail from "components/StudySnapshot/StudySnapshotDetail";
import RigorousJournalTag from "components/Tag/RigorousJournalTag";
import VeryRigourousJournalTag from "components/Tag/VeryRigorousJournalTag";
import Tooltip from "components/Tooltip";
import CreateBookmarkItemTooltip from "components/Tooltip/CreateBookmarkItemTooltip/CreateBookmarkItemTooltip";
import { PoweredBySciScore } from "components/Tooltip/RigorousJournalTooltip/RigorousJournalTooltip";
import VerticalDivider from "components/VerticalDivider";
import { MAX_VISIBLE_AUTHORS } from "constants/config";
import { FeatureFlag } from "enums/feature-flag";
import { Badges } from "helpers/api";
import useIsFeatureEnabled from "hooks/useIsFeatureEnabled";
import useLabels from "hooks/useLabels";
import { useState } from "react";
import Quartile from "./Quartile";

export interface IDetailItem {
  claim?: {
    id: string;
    text: string;
    url_slug: string;
  } | null;
  paper: {
    abstract: string;
    abstract_takeaway: string;
    publish_date: string;
    authors: string[];
    badges: Badges;
    citation_count: number;
    doi?: string;
    id: string;
    journal: {
      scimago_quartile: number | undefined;
      title: string;
    };
    pages: string;
    provider_url: string;
    title: string;
    volume: string;
    url_slug: string | null;
    year: number;
  };
}

type DetailContentProps = {
  handleClickCite: () => void;
  handleClickFullTextLink: () => void;
  handleClickSave: () => void;
  handleClickShare: () => void;
  isBookmarked: boolean;
  isLimitedBookmarkItem: boolean | undefined;
  item: IDetailItem;
};

function DetailContent({
  handleClickCite,
  handleClickFullTextLink,
  handleClickSave,
  handleClickShare,
  isBookmarked,
  isLimitedBookmarkItem,
  item,
}: DetailContentProps) {
  const [showMoreAuthors, setShowMoreAuthors] = useState(false);
  const [openAccessPdf] = useState();

  const features = {
    bookmark: useIsFeatureEnabled(FeatureFlag.BOOKMARK),
    studySnapShot: useIsFeatureEnabled(FeatureFlag.STUDY_SNAPSHOT),
  };

  const [pageLabels] = useLabels("screens.details");

  const badgesRender: any[] = [];
  if (item.paper.badges?.very_rigorous_journal === true) {
    badgesRender.push(<VeryRigourousJournalTag key="very_rigorous_journal" />);
  }

  if (item.paper.badges?.rigorous_journal === true) {
    badgesRender.push(<RigorousJournalTag key="rigorous_journal" />);
  }

  return (
    <>
      <ResultDetailDoi doi={item.paper.doi} />
      <div className="flex justify-between bg-white rounded-2xl flex-nowrap detail-content">
        <div
          data-testid="result-paper"
          className="w-full detail-content-left pt-5 lg:pt-8 lg:pb-8 lg:border-r border-r-gray-200 px-5 lg:px-8"
        >
          <h1
            data-testid="paper-title"
            className="mb-2 text-xl font-bold text-black md:text-2xl"
          >
            {item.paper?.title}
          </h1>
          {item.paper?.authors?.length > 0 ? (
            <div className="flex flex-row items-center gap-x-2">
              <Icon
                size={16}
                className="text-gray-550 w-4 min-w-[16px]"
                name="users"
              />
              <div className="text-sm text-gray-550">
                {showMoreAuthors ? (
                  <p data-testid="show-more-author">
                    {(item.paper?.authors || []).map(
                      (author: string, index: number) => {
                        if (index === 0) return author;
                        return `, ${author}`;
                      }
                    )}
                  </p>
                ) : (
                  <p data-testid="hide-more-author">
                    {(item.paper?.authors || [])
                      .slice(0, MAX_VISIBLE_AUTHORS)
                      .map((author: string, index: number) => {
                        if (index === 0) return author;
                        return `, ${author}`;
                      })}{" "}
                    {(item.paper?.authors || []).length - MAX_VISIBLE_AUTHORS >
                      0 && (
                      <button
                        data-testid="more-author-button"
                        onClick={() => setShowMoreAuthors(true)}
                        className="text-green-600"
                      >
                        +{" "}
                        {(item.paper?.authors || []).length -
                          MAX_VISIBLE_AUTHORS}{" "}
                        more authors
                      </button>
                    )}
                  </p>
                )}
              </div>
            </div>
          ) : null}
          <div className="flex flex-row items-center gap-x-2 mt-[6px]">
            <Icon
              size={16}
              className="text-gray-550 w-4 min-w-[16px]"
              name="calendar"
            />
            <p className="text-sm text-gray-550">{item.paper.year}</p>
          </div>
          <div className="flex justify-start items-center space-x-3 mt-[18px]">
            {features.bookmark && (
              <>
                <Tooltip
                  interactive
                  maxWidth={340}
                  onShown={(instance: any) => {}}
                  onHidden={(instance: any) => {}}
                  tooltipContent={<CreateBookmarkItemTooltip />}
                  className="rounded-xl premium-bookmark-popup"
                  disabled={isLimitedBookmarkItem !== true || isBookmarked}
                >
                  <button
                    className="flex items-center text-sm font-bold text-black whitespace-nowrap"
                    onClick={handleClickSave}
                  >
                    {isBookmarked ? (
                      <>
                        <img
                          alt="bookmark"
                          src="/icons/bookmark-blue.svg"
                          className="w-5 h-5 mr-2"
                        />
                        Saved
                      </>
                    ) : (
                      <>
                        <img
                          alt="bookmark"
                          src="/icons/bookmark-outline-blue.svg"
                          className="w-5 h-5 mr-2"
                        />
                        Save
                      </>
                    )}
                  </button>
                </Tooltip>
                <VerticalDivider />
              </>
            )}
            <button
              className="flex items-center text-sm font-bold text-black whitespace-nowrap"
              onClick={handleClickCite}
            >
              <img
                className="w-5 h-5 mr-2"
                alt="Cite"
                src="/icons/quotation-mark.svg"
              />
              {pageLabels["cite"]}
            </button>
            <VerticalDivider />
            <button
              data-testid="share-detail"
              className="flex items-center text-sm font-bold text-black whitespace-nowrap"
              onClick={handleClickShare}
            >
              <img
                alt="share"
                src="/icons/share.svg"
                className="w-5 h-5 mr-2"
              />
              Share
            </button>
          </div>
          <div className="w-full h-[1px] bg-gray-200 my-[26px]" />
          <ResultDetailItemExtras
            journal={item.paper.journal.title}
            provider_url={item.paper.provider_url}
            citation_count={item.paper.citation_count}
            year={item.paper.year}
            isDetail
            badges={item.paper.badges}
          />
          {features.studySnapShot && (
            <div className="my-[26px]">
              <StudySnapshotDetail
                paperId={item.paper.id}
                isDetailPage={true}
                badges={item.paper.badges}
              />
            </div>
          )}
          <div className="flex flex-col items-start sm:flex-row sm:gap-y-0 gap-y-3">
            <div className="min-w-[71px]">
              <p data-testid="result-journal" className="text-sm text-gray-500">
                {pageLabels["journal"]}
              </p>
            </div>
            <div className="flex flex-col gap-y-2">
              <p data-testid="journal-title" className="text-base text-black">
                {item.paper.journal?.title || pageLabels["empty-journal-name"]}
              </p>
              <Quartile
                quartile={item.paper.journal.scimago_quartile || null}
              />
              {badgesRender.length > 0 ? (
                <div className="flex items-center gap-2 flex-wrap">
                  {badgesRender}
                  <PoweredBySciScore size="small" />
                </div>
              ) : null}
            </div>
          </div>
        </div>
        <div className="w-full h-[1px] lg:hidden bg-gray-200 my-[26px]" />
        <div className="lg:flex-grow">
          <div className="w-full px-5 pb-5 lg:pb-8 lg:pt-8 lg:px-8">
            <div className="flex flex-row items-center gap-x-4">
              {item.paper?.doi ? (
                <a
                  data-testid="full-text-link"
                  href={`https://doi.org/${item.paper.doi}`}
                  target="_blank"
                  className="flex items-center text-sm font-bold text-black whitespace-nowrap"
                  rel="noreferrer"
                  onClick={handleClickFullTextLink}
                >
                  <img
                    className="w-5 h-5 mr-2"
                    alt="Open in new"
                    src="/icons/open-in-new.svg"
                  />
                  {pageLabels["view-full-text"]}
                </a>
              ) : null}
              <a
                data-testid="semantic-scholar-link"
                href={item.paper.provider_url}
                target="_blank"
                className="flex items-center text-sm font-bold text-black whitespace-nowrap"
                rel="noreferrer"
              >
                <img
                  className="w-5 h-5 mr-1"
                  alt="Semantic Scholar"
                  src="/icons/semantic-scholar.svg"
                />
                {pageLabels["semantic-scholar"]}
              </a>
              {openAccessPdf ? (
                <a
                  href="#"
                  target="_blank"
                  className="flex items-center text-sm font-bold text-black whitespace-nowrap"
                  rel="noreferrer"
                >
                  <img
                    className="w-4 h-4 mr-2"
                    alt="PDF"
                    src="/icons/pdf.svg"
                  />
                  {pageLabels["pdf"]}
                </a>
              ) : null}
            </div>
            <div
              data-testid="result-claim"
              className="rounded-xl p-5 bg-gray-100 my-5 sm:my-[26px] flex flex-col sm:flex-row"
            >
              <div className="flex flex-row items-center mb-3 sm:items-start sm:mb-0">
                <img
                  className="min-w-[24px] max-w-[24px] h-6 w-6 mr-[6px]"
                  alt="Sparkler"
                  src="/icons/sparkler.svg"
                />
                <strong className="sm:hidden">
                  {pageLabels["key-takeaway"]}{" "}
                </strong>
              </div>
              <div className="flex flex-grow">
                <h2 className="text-base text-green-650">
                  <strong className="hidden sm:contents">
                    {pageLabels["key-takeaway"]}:{" "}
                  </strong>
                  {item.claim?.text || item.paper.abstract_takeaway}
                </h2>
              </div>
            </div>
            <div>
              <p className="mb-2 text-sm text-gray-500">
                {pageLabels["abstract"]}
              </p>
              <p
                className="text-base text-black"
                data-testid="abstract"
                dangerouslySetInnerHTML={{
                  __html: item.paper?.abstract,
                }}
              ></p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default DetailContent;
