import AnimalTrialTag from "components/Tag/AnimalTrialTag";
import CaseStudyTag from "components/Tag/CaseStudyTag";
import DisputedPaperTag from "components/Tag/DisputedPaperTag";
import HighlyCitedTag from "components/Tag/HighlyCitedTag";
import InVitroTrialTag from "components/Tag/InVitroTrialTag";
import LargeHumanTrialTag from "components/Tag/LargeHumanTrialTag";
import LiteratureReviewTag from "components/Tag/LiteratureReviewTag";
import MetaAnalysisTag from "components/Tag/MetaAnalysisTag";
import NonRctTrialTag from "components/Tag/NonRctTrialTag";
import ObservationalStudyTag from "components/Tag/ObservationalStudyTag";
import RctTag from "components/Tag/RctTag";
import RigorousJournalTag from "components/Tag/RigorousJournalTag";
import SystematicReviewTag from "components/Tag/SystematicReviewTag";
import VeryRigourousJournalTag from "components/Tag/VeryRigorousJournalTag";
import Tooltip from "components/Tooltip";
import VerticalDivider from "components/VerticalDivider";
import { Badges, StudyType } from "helpers/api";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import React, { Fragment } from "react";

export type ResultDetailItemExtrasProps = {
  id?: string;
  journal?: string;
  provider_url?: string;
  primary_author?: string;
  citation_count?: number;
  year?: number;
  isDetail?: boolean;
  badges?: Badges;
  isLoadingStudyType?: boolean;
};

/**
 * @component ResultDetailExtras
 * @description Detail extras for result page
 * @example
 * return (
 *   <ResultDetailExtras journal="journal" year={2022} />
 * )
 */
const ResultDetailExtras = ({
  id,
  year,
  citation_count,
  provider_url,
  journal,
  primary_author,
  isDetail,
  badges,
  isLoadingStudyType,
}: ResultDetailItemExtrasProps) => {
  const [pageLabels] = useLabels("screens.details");
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  const badgesRender: any[] = [];

  if (badges?.disputed && badges.disputed.reason && badges.disputed.url) {
    badgesRender.push(
      <DisputedPaperTag
        key="disputed"
        reason={badges.disputed.reason}
        url={badges.disputed.url}
      />
    );
  }

  if (badges?.study_type === StudyType.RCT) {
    badgesRender.push(<RctTag key="rct" />);
  }

  if (badges?.study_type === StudyType.META_ANALYSIS) {
    badgesRender.push(<MetaAnalysisTag key="meta_analysis" />);
  }

  if (badges?.study_type === StudyType.SYSTEMATIC_REVIEW) {
    badgesRender.push(<SystematicReviewTag key="systemic_review" />);
  }

  if (badges?.study_type === StudyType.CASE_STUDY) {
    badgesRender.push(<CaseStudyTag key="case_study" />);
  }

  if (badges?.study_type === StudyType.NON_RCT_TRIAL) {
    badgesRender.push(<NonRctTrialTag key="non_rct_trial" />);
  }

  if (badges?.study_type === StudyType.OBSERVATIONAL_STUDY) {
    badgesRender.push(<ObservationalStudyTag key="observational_study" />);
  }

  if (badges?.study_type === StudyType.LITERATURE_REVIEW) {
    badgesRender.push(<LiteratureReviewTag key="literature_review" />);
  }

  if (badges?.study_type === StudyType.IN_VITRO_TRIAL) {
    badgesRender.push(<InVitroTrialTag key="in_vitro_trial" />);
  }

  if (badges?.animal_trial === true) {
    badgesRender.push(<AnimalTrialTag key="animal_trial" />);
  }

  if (badges?.large_human_trial === true) {
    badgesRender.push(<LargeHumanTrialTag key="large_human_trial" />);
  }

  if (!isDetail && badges?.very_rigorous_journal === true) {
    badgesRender.push(<VeryRigourousJournalTag key="very_rigorous_journal" />);
  }

  if (!isDetail && badges?.rigorous_journal === true) {
    badgesRender.push(<RigorousJournalTag key="rigorous_journal" />);
  }

  if (badges?.highly_cited_paper === true) {
    badgesRender.push(
      <HighlyCitedTag key="highly_cited_paper" isDetail={isDetail} />
    );
  }

  if (isDetail) {
    return (
      <div
        data-testid="result-detail-extras"
        className="flex flex-col items-start sm:gap-y-5 gap-y-[26px]"
      >
        <div className="flex flex-col items-start sm:flex-row sm:gap-y-0 gap-y-3">
          <div className="min-w-[136px]">
            <p className="text-sm text-[#808993]">{pageLabels["citations"]}</p>
          </div>
          <div className="flex flex-row gap-x-[6px]">
            <p className="font-bold text-[#364B44]">{citation_count}</p>
            <p className="text-[#364B44]">{pageLabels["citations"]}</p>
          </div>
        </div>
        {badgesRender && badgesRender.length > 0 ? (
          <div className="flex flex-col items-start sm:flex-row sm:gap-y-0 gap-y-3">
            <div className="min-w-[136px]">
              <p className="text-sm text-[#808993]">
                {pageLabels["quality-indicators"]}
              </p>
            </div>
            <div className="flex flex-col items-start justify-start gap-y-3">
              {badgesRender.map((item) => item)}
            </div>
          </div>
        ) : null}
      </div>
    );
  }

  return (
    <div
      data-testid="result-detail-extras"
      className={`items-center ${isDetail ? "lg:flex w-full" : ""}`}
    >
      {!isDetail && isMobile && journal && (
        <Tooltip
          delay={1000}
          disabled={isMobile}
          tooltipContent={<p>{journal}</p>}
        >
          <p
            data-testid="detail-extras-journal"
            className={`md:hidden text-gray-400 text-xs sm:text-sm content mb-[6px] md:mb-0 max-w-xs`}
          >
            {journal}
          </p>
        </Tooltip>
      )}
      <div
        className={`text-gray-400 ${
          isDetail ? "text-sm" : "text-xs"
        } sm:text-sm flex mr-6`}
      >
        {!isDetail ? (
          <div className="hidden md:flex">
            {journal && (
              <Tooltip
                delay={1000}
                disabled={isMobile}
                tooltipContent={<p>{journal}</p>}
              >
                <p
                  data-testid="detail-extras-journal"
                  className={`text-gray-400 text-xs sm:text-sm content mb-1 md:mb-0 ${
                    isDetail ? "" : "max-w-[200px] lg:max-w-lg"
                  }`}
                >
                  {journal}
                </p>
              </Tooltip>
            )}
            {journal && (
              <div
                data-testid="detail-extras-journal-separator"
                className="block mx-3"
              >
                <VerticalDivider />
              </div>
            )}
          </div>
        ) : null}
        {primary_author && (
          <Tooltip
            delay={1000}
            disabled={isMobile}
            tooltipContent={
              <p>
                {primary_author} {pageLabels["et-al"]}
              </p>
            }
          >
            <p
              data-testid="detail-extras-author"
              className="mr-2 sm:mr-3 content"
            >
              {primary_author} {pageLabels["et-al"]}
            </p>
          </Tooltip>
        )}{" "}
        {primary_author && year ? (
          <div className="mr-2 sm:mr-3">
            <VerticalDivider />
          </div>
        ) : (
          ""
        )}{" "}
        {typeof citation_count === "number" && (
          <p className="mr-2 sm:mr-3 whitespace-nowrap lowercase">
            <span data-testid="detail-extras-citation" className="text-black">
              {citation_count}
            </span>{" "}
            {pageLabels["citations"]}
          </p>
        )}{" "}
        {typeof citation_count === "number" && year ? (
          <div className="mr-2 sm:mr-3">
            <VerticalDivider />
          </div>
        ) : (
          ""
        )}{" "}
        {year}
      </div>
      {!isDetail ? (
        <div
          className={`flex flex-col md:flex-row items-start md:items-center gap-[6px] sm:gap-3 flex-wrap ${
            badgesRender.length > 0 ? "mb-0 mt-3 md:mt-5" : ""
          }`}
        >
          {badgesRender.map((item, index) => (
            <Fragment key={item.key}>
              {item}
              {badgesRender.length - 1 !== index ? (
                <div className="hidden md:block">
                  <VerticalDivider />
                </div>
              ) : null}
            </Fragment>
          ))}
          {isLoadingStudyType ? (
            <div className="flex flex-wrap items-center animate-pulse">
              <div className="mr-4 mb-3 sm:mb-0 bg-[#F1F4F6] h-3 w-[237px] md:w-[161px] rounded-xl" />
              <div className="mr-4 mb-3 sm:mb-0 w-[1px] h-[17px] bg-[#DEE0E3] hidden md:block" />
              <div className="mr-4 bg-[#F1F4F6] h-3 w-[104px] rounded-xl" />
              <div className="mr-4 w-[1px] h-[17px] bg-[#DEE0E3]" />
              <div className="mr-4 bg-[#F1F4F6] h-3 w-[37px] rounded-xl" />
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
};

export default ResultDetailExtras;
