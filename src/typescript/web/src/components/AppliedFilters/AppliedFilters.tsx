import {
  optionsDomain,
  optionsStudyTypes,
} from "components/FilterDrawer/FilterDrawer";
import Icon from "components/Icon";
import { ResultPageParams } from "helpers/pageUrl";
import useLabels from "hooks/useLabels";
import { useMemo } from "react";

export type TFilter = {
  label: string;
  value?: string;
  type:
    | "year"
    | "study-type"
    | "controlled"
    | "human"
    | "sample-size"
    | "sjr-quartile"
    | "domain";
};

export function getSearchFiltersFromParam(value: ResultPageParams) {
  const filters: TFilter[] = [];
  if (value?.yearMin) {
    filters.push({
      label: `${value.yearMin}-now`,
      value: value.yearMin,
      type: "year",
    });
  }
  if (value?.studyTypes) {
    value.studyTypes.split(",").forEach((filter) => {
      const studyType = optionsStudyTypes.find((item) => item.value === filter);
      if (studyType) {
        filters.push({
          label: studyType.label,
          value: studyType.value,
          type: "study-type",
        });
      }
    });
  }
  if (value?.filterControlledStudies === "true") {
    filters.push({
      label: "Controlled",
      type: "controlled",
    });
  }
  if (value?.filterHumanStudies === "true") {
    filters.push({
      label: "Humans",
      type: "human",
    });
  }
  if (value?.sampleSizeMin) {
    const sampleSizeValue = Number(value.sampleSizeMin);
    if (typeof sampleSizeValue === "number") {
      filters.push({
        label: `Sample size ≥ ${sampleSizeValue}`,
        type: "sample-size",
      });
    }
  }
  if (value?.sjrBestQuartileMin && value?.sjrBestQuartileMax) {
    if (value.sjrBestQuartileMin === value.sjrBestQuartileMax) {
      filters.push({
        label: `Q${value.sjrBestQuartileMin} Journals`,
        type: "sjr-quartile",
      });
    } else {
      filters.push({
        label: `Q${value.sjrBestQuartileMin}-Q${value.sjrBestQuartileMax} Journals`,
        type: "sjr-quartile",
      });
    }
  }
  if (value?.fieldsOfStudy) {
    value.fieldsOfStudy.split(",").forEach((filter) => {
      const domain = optionsDomain.find((item) => item.value === filter);
      if (domain) {
        filters.push({
          label: domain.label,
          value: domain.value,
          type: "domain",
        });
      }
    });
  }
  return filters;
}

type Props = {
  value: ResultPageParams;
  onChangeFilter: (value: ResultPageParams) => void;
};

const AppliedFilters = ({ value, onChangeFilter }: Props) => {
  const [generalLabels] = useLabels("general");

  const applieFilters = useMemo(() => {
    const filters: TFilter[] = getSearchFiltersFromParam(value);
    return filters;
  }, [value]);

  if (applieFilters.length === 0) {
    return null;
  }

  const handleRemoveFilter = (filter: TFilter) => {
    let newSelectedStudyTypes = value?.studyTypes;
    let newSelectedDomains = value?.fieldsOfStudy;

    if (filter.type === "study-type") {
      const listSelectedStudyTypes = value?.studyTypes?.split(",") || [];
      newSelectedStudyTypes = listSelectedStudyTypes
        .filter((studyType) => studyType !== filter.value)
        .toString();
    }
    if (filter.type === "domain") {
      const listSelectedDomains = value?.fieldsOfStudy?.split(",") || [];
      newSelectedDomains = listSelectedDomains
        .filter((domain) => domain !== filter.value)
        .toString();
    }

    onChangeFilter({
      studyTypes: newSelectedStudyTypes,
      fieldsOfStudy: newSelectedDomains,
      filterControlledStudies:
        filter.type === "controlled" ? "" : value?.filterControlledStudies,
      filterHumanStudies:
        filter.type === "human" ? "" : value?.filterHumanStudies,
      sampleSizeMin: filter.type === "sample-size" ? "" : value?.sampleSizeMin,
      sjrBestQuartileMin:
        filter.type === "sjr-quartile" ? "" : value?.sjrBestQuartileMin,
      sjrBestQuartileMax:
        filter.type === "sjr-quartile" ? "" : value?.sjrBestQuartileMax,
      yearMin: filter.type === "year" ? "" : value?.yearMin,
    });
  };

  return (
    <div className="flex flex-row items-center gap-3 text-[#364B44] mt-5 flex-wrap">
      <span className="mr-[8px]">{generalLabels["applied-filters"]}:</span>
      {applieFilters.map((filter, filterIdx) => (
        <div
          key={filterIdx}
          className="h-8 px-[8px] border border-[#DEE0E3] rounded-[21px] bg-white flex flex-row items-center justify-between"
        >
          <span className="mr-[8px]">{filter.label}</span>
          <button
            data-testid="close-input"
            onClick={() => handleRemoveFilter(filter)}
            type="button"
            className="bg-[#EDF0F2] hover:bg-gray-200 h-5 w-5 flex justify-center items-center rounded-full"
          >
            <Icon className="text-gray-500 h-4 w-4" name="x" />
          </button>
        </div>
      ))}
    </div>
  );
};

export default AppliedFilters;
