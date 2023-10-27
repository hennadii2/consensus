import { Disclosure } from "@headlessui/react";
import {
  getSearchFiltersFromParam,
  TFilter,
} from "components/AppliedFilters/AppliedFilters";
import Drawer from "components/Drawer";
import Icon from "components/Icon";
import Switch from "components/Switch";
import AnimalTrialTag from "components/Tag/AnimalTrialTag";
import CaseStudyTag from "components/Tag/CaseStudyTag";
import InVitroTrialTag from "components/Tag/InVitroTrialTag";
import LiteratureReviewTag from "components/Tag/LiteratureReviewTag";
import MetaAnalysisTag from "components/Tag/MetaAnalysisTag";
import NonRctTrialTag from "components/Tag/NonRctTrialTag";
import ObservationalStudyTag from "components/Tag/ObservationalStudyTag";
import RctTag from "components/Tag/RctTag";
import SystematicReviewTag from "components/Tag/SystematicReviewTag";
import Tooltip from "components/Tooltip";
import SjrQuartilesTooltip from "components/Tooltip/SjrQuartilesTooltip/SjrQuartilesTooltip";
import StudyDetailsFilterTooltip from "components/Tooltip/StudyDetailsFilterTooltip/StudyDetailsFilterTooltip";
import StudyTypesFilterTooltip from "components/Tooltip/StudyTypesFilterTooltip/StudyTypesFilterTooltip";
import { ResultPageParams } from "helpers/pageUrl";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import { useEffect, useMemo, useState } from "react";

type FilterDrawerProps = {
  open?: boolean;
  children?: React.ReactNode;
  onClose: () => void;
  value: ResultPageParams;
  onChangeFilter: (value: ResultPageParams) => void;
};

function FilterDrawer({
  open,
  onClose,
  value,
  onChangeFilter,
}: FilterDrawerProps) {
  const [filterLabels] = useLabels("filter");
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  const [selectedYear, setSelectedYear] = useState(
    value?.yearMin || filterLabels["all-years"]
  );
  const [selectedStudyTypes, setSelectedStudyTypes] = useState(
    value?.studyTypes || ""
  );
  const [controlledStudies, setControlledStudies] = useState(
    value?.filterControlledStudies === "true"
      ? true
      : value?.filterControlledStudies === "false"
      ? false
      : ""
  );
  const [humanStudies, setHumanStudies] = useState(
    value?.filterHumanStudies === "true"
      ? true
      : value?.filterHumanStudies === "false"
      ? false
      : ""
  );
  const [sampleSize, setSampleSize] = useState(value?.sampleSizeMin || "");
  const [sjrQuartileMin, setSjrQuartileMin] = useState(
    Number(value?.sjrBestQuartileMin) || ""
  );
  const [sjrQuartileMax, setSjrQuartileMax] = useState(
    Number(value?.sjrBestQuartileMax) || ""
  );
  const [selectedDomains, setSelectedDomains] = useState(
    value?.fieldsOfStudy || ""
  );

  const optionsYear = useMemo(() => {
    const years = ["2018", "2015", "2010", "2005", "2000", "1990"];

    // generate current year - 1
    const thisYear = new Date().getFullYear();
    for (let index = Number(years[0]) + 1; index <= thisYear; index++) {
      years.unshift(index.toString());
    }

    return years;
  }, []);

  const countFilters = useMemo(() => {
    const filters: TFilter[] = getSearchFiltersFromParam(value);
    return filters;
  }, [value]);

  const [searchResultDomains, setSearchResultDomains] =
    useState<typeof optionsDomain>(optionsDomain);

  useEffect(() => {
    setSelectedYear(value.yearMin || filterLabels["all-years"]);
  }, [filterLabels, value.yearMin]);

  useEffect(() => {
    setSelectedStudyTypes(value.studyTypes || "");
  }, [filterLabels, value.studyTypes]);

  useEffect(() => {
    setControlledStudies(
      value.filterControlledStudies === "true"
        ? true
        : value?.filterControlledStudies === "false"
        ? false
        : ""
    );
  }, [filterLabels, value.filterControlledStudies]);

  useEffect(() => {
    setHumanStudies(
      value.filterHumanStudies === "true"
        ? true
        : value?.filterHumanStudies === "false"
        ? false
        : ""
    );
  }, [filterLabels, value.filterHumanStudies]);

  useEffect(() => {
    setSampleSize(value.sampleSizeMin || "");
  }, [filterLabels, value.sampleSizeMin]);

  useEffect(() => {
    setSjrQuartileMin(Number(value.sjrBestQuartileMin) || "");
    setSjrQuartileMax(Number(value.sjrBestQuartileMax) || "");
  }, [filterLabels, value.sjrBestQuartileMin, value.sjrBestQuartileMax]);

  useEffect(() => {
    setSelectedDomains(value.fieldsOfStudy || "");
  }, [value.fieldsOfStudy, filterLabels]);

  const handleChangeYear = (value: string) => {
    setSelectedYear(value);
  };

  const handleChangeStudyTypes = (value: string) => {
    let isSelected = false;
    let listSelectedStudyTypes: string[] = [];
    if (selectedStudyTypes !== "") {
      listSelectedStudyTypes = selectedStudyTypes.split(",");
      isSelected = listSelectedStudyTypes.includes(value);
    }
    let newSelectedStudyTypes = "";
    if (isSelected) {
      newSelectedStudyTypes = listSelectedStudyTypes
        .filter((studyType) => studyType !== value)
        .toString();
    } else {
      listSelectedStudyTypes.push(value);
      newSelectedStudyTypes = listSelectedStudyTypes.toString();
    }
    setSelectedStudyTypes(newSelectedStudyTypes);
  };

  const handleChangeDomains = (value: string) => {
    let isSelected = false;
    let listSelectedDomains: string[] = [];
    if (selectedDomains !== "") {
      listSelectedDomains = selectedDomains.split(",");
      isSelected = listSelectedDomains.includes(value);
    }
    let newSelectedDomains = "";
    if (isSelected) {
      newSelectedDomains = listSelectedDomains
        .filter((studyType) => studyType !== value)
        .toString();
    } else {
      listSelectedDomains.push(value);
      newSelectedDomains = listSelectedDomains.toString();
    }
    setSelectedDomains(newSelectedDomains);
  };

  const handleSearchDomains = (domain: string) => {
    if (domain) {
      const resultDomains = optionsDomain.filter((item) =>
        item.label.toLowerCase().includes(domain.toLowerCase())
      );
      setSearchResultDomains(resultDomains);
    } else {
      setSearchResultDomains(optionsDomain);
    }
  };

  const handleApply = () => {
    onChangeFilter({
      yearMin: selectedYear,
      studyTypes: selectedStudyTypes,
      filterControlledStudies: controlledStudies?.toString(),
      filterHumanStudies: humanStudies?.toString(),
      sampleSizeMin: sampleSize,
      sjrBestQuartileMin:
        sjrQuartileMin?.toString() === "1" && sjrQuartileMax?.toString() === "4"
          ? ""
          : sjrQuartileMin?.toString(),
      sjrBestQuartileMax:
        sjrQuartileMin?.toString() === "1" && sjrQuartileMax?.toString() === "4"
          ? ""
          : sjrQuartileMax?.toString(),
      fieldsOfStudy: selectedDomains,
    });
    onClose();
  };

  const handleReset = () => {
    onChangeFilter({
      yearMin: filterLabels["all-years"],
      studyTypes: "",
      filterControlledStudies: "",
      filterHumanStudies: "",
      sampleSizeMin: "",
      sjrBestQuartileMin: "",
      sjrBestQuartileMax: "",
      fieldsOfStudy: "",
    });
    onClose();
  };

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title={`Filters${
        countFilters.length > 0 ? ` (${countFilters.length})` : ""
      }`}
    >
      <div data-testid="filter-drawer">
        <Disclosure defaultOpen={!isMobile}>
          {({ open }) => (
            <>
              <Disclosure.Button
                className={`flex w-full justify-between text-base text-[#222F2B]`}
              >
                <span>{filterLabels["published-since"]}</span>
                {open ? (
                  <Icon size={24} name="chevron-up" />
                ) : (
                  <Icon size={24} name="chevron-down" />
                )}
              </Disclosure.Button>
              <Disclosure.Panel className="pt-4 columns-2">
                {[filterLabels["all-years"], ...optionsYear].map(
                  (option, optionIdx) => (
                    <button
                      onClick={() => handleChangeYear(option)}
                      key={optionIdx}
                      className={`w-full py-[6px] px-5 text-left rounded-[26px] mb-1 ${
                        selectedYear === option
                          ? "bg-[#EFFCF8] text-[#27B196]"
                          : "text-[#222F2B]"
                      }`}
                    >
                      <span className="leading-[24px]">{option}</span>
                    </button>
                  )
                )}
              </Disclosure.Panel>
            </>
          )}
        </Disclosure>
        <div className="h-[1px] bg-[#DEE0E3] w-full my-5" />
        <Disclosure defaultOpen={!isMobile && selectedStudyTypes !== ""}>
          {({ open }) => (
            <>
              <Disclosure.Button
                className={`flex w-full justify-between text-base text-[#222F2B]`}
              >
                <div className="flex flex-row items-center">
                  <img
                    className="min-w-[24px] max-w-[24px] h-6 w-6 ml-1 mr-[6px]"
                    alt="Sparkler"
                    src="/icons/sparkler.svg"
                  />
                  <span className="mr-2">{filterLabels["study-types"]}</span>
                  <Tooltip
                    interactive
                    maxWidth={334}
                    tooltipContent={<StudyTypesFilterTooltip />}
                  >
                    <img
                      className="min-w-[16px] max-w-[16px] h-4"
                      alt="Info"
                      src="/icons/info.svg"
                    />
                  </Tooltip>
                </div>
                {open ? (
                  <Icon size={24} name="chevron-up" />
                ) : (
                  <Icon size={24} name="chevron-down" />
                )}
              </Disclosure.Button>
              <Disclosure.Panel className="pt-4 flex-col flex items-start">
                {optionsStudyTypes.map((option, optionIdx) => {
                  const isSelected = selectedStudyTypes
                    .split(",")
                    .find((item) => item === option.value);
                  return (
                    <button
                      onClick={() => handleChangeStudyTypes(option.value)}
                      key={optionIdx}
                      className="mb-3 flex flex-row items-center"
                    >
                      <img
                        className={`w-4 h-4 mr-3 rounded-sm ${
                          isSelected ? "bg-[#0A6DC2]" : ""
                        }`}
                        alt="checked"
                        src={
                          isSelected
                            ? "/icons/checked.svg"
                            : "/icons/unchecked.svg"
                        }
                      />
                      {option.elementTag}
                    </button>
                  );
                })}
              </Disclosure.Panel>
            </>
          )}
        </Disclosure>
        <div className="h-[1px] bg-[#DEE0E3] w-full my-5" />
        <Disclosure
          defaultOpen={
            (!isMobile && controlledStudies === true) ||
            humanStudies === true ||
            sampleSize !== ""
          }
        >
          {({ open }) => (
            <>
              <Disclosure.Button
                className={`flex w-full justify-between text-base text-[#222F2B]`}
              >
                <div className="flex flex-row items-center">
                  <img
                    className="min-w-[24px] max-w-[24px] h-6 w-6 ml-1 mr-[6px]"
                    alt="Sparkler"
                    src="/icons/sparkler.svg"
                  />
                  <span className="mr-2">{filterLabels["study-details"]}</span>
                  <Tooltip
                    interactive
                    maxWidth={334}
                    tooltipContent={<StudyDetailsFilterTooltip />}
                  >
                    <img
                      className="min-w-[16px] max-w-[16px] h-4"
                      alt="Info"
                      src="/icons/info.svg"
                    />
                  </Tooltip>
                </div>
                {open ? (
                  <Icon size={24} name="chevron-up" />
                ) : (
                  <Icon size={24} name="chevron-down" />
                )}
              </Disclosure.Button>
              <Disclosure.Panel className="pt-4 flex-col flex items-start">
                <div className="flex flex-row items-center max-w-[172px] w-full justify-between text-[#364B44]">
                  <span>{filterLabels["controlled-studies"]}</span>
                  <Switch
                    active={
                      typeof controlledStudies === "string"
                        ? false
                        : controlledStudies
                    }
                    onChange={(value) => setControlledStudies(value || "")}
                  />
                </div>
                <div className="flex flex-row items-center max-w-[172px] w-full justify-between text-[#364B44] mt-3">
                  <span>{filterLabels["human-studies"]}</span>
                  <Switch
                    active={
                      typeof humanStudies === "string" ? false : humanStudies
                    }
                    onChange={(value) => setHumanStudies(value || "")}
                  />
                </div>
                <div className="flex flex-row items-center w-full justify-between text-[#364B44] mt-3">
                  <span className="w-[115px] min-w-[115px] mr-[23px]">
                    {filterLabels["sample-size"]}&nbsp;&nbsp;&nbsp;≥
                  </span>
                  <input
                    placeholder="min 1"
                    className="p-2 border-[#DEE0E3] border rounded-md h-[35px] w-full"
                    type="number"
                    min={1}
                    value={sampleSize}
                    onChange={(e) => setSampleSize(e.target.value)}
                  />
                </div>
              </Disclosure.Panel>
            </>
          )}
        </Disclosure>
        <div className="h-[1px] bg-[#DEE0E3] w-full my-5" />
        <Disclosure
          defaultOpen={
            !isMobile && sjrQuartileMin !== "" && sjrQuartileMax !== ""
          }
        >
          {({ open }) => (
            <>
              <Disclosure.Button
                className={`flex w-full justify-between text-base text-[#222F2B]`}
              >
                <span>{filterLabels["journals"]}</span>
                {open ? (
                  <Icon size={24} name="chevron-up" />
                ) : (
                  <Icon size={24} name="chevron-down" />
                )}
              </Disclosure.Button>
              <Disclosure.Panel className="pt-4 flex-col flex items-start">
                <div className="flex flex-row items-center gap-x-2">
                  <span className="text-[#688092] text-sm">
                    {filterLabels["sjr-quartile-rating"]}
                  </span>
                  <Tooltip
                    interactive
                    maxWidth={334}
                    tooltipContent={<SjrQuartilesTooltip />}
                  >
                    <img
                      className="min-w-[16px] max-w-[16px] h-4"
                      alt="Info"
                      src="/icons/info.svg"
                    />
                  </Tooltip>
                </div>
                <div className="w-full gap-x-2 pt-4 flex flex-row">
                  {[1, 2, 3, 4].map((item) => (
                    <button
                      onClick={() => {
                        if (Number(sjrQuartileMax) === 1 && item === 1) {
                          setSjrQuartileMin("");
                          setSjrQuartileMax("");
                        } else {
                          if (Number(sjrQuartileMax) == item) {
                            setSjrQuartileMin(1);
                            setSjrQuartileMax(item - 1);
                          } else {
                            setSjrQuartileMin(1);
                            setSjrQuartileMax(item);
                          }
                        }
                      }}
                      key={item}
                      className={`flex flex-row rounded-full h-[27px] px-[9px] items-center border ${
                        item <= Number(sjrQuartileMax)
                          ? "bg-[#085394] border-[#085394]"
                          : "border-[#D9D9D9]"
                      }`}
                    >
                      <div
                        className={`h-2 rounded-full w-5 mr-[6px] ${
                          item === 1
                            ? "bg-[#46A759]"
                            : item === 4
                            ? "bg-[#E3504F]"
                            : "bg-[#FFB800]"
                        }`}
                      />
                      <span
                        className={`text-xs ${
                          item <= Number(sjrQuartileMax)
                            ? "text-white"
                            : "text-[#222F2B]"
                        }`}
                      >
                        Q{item}
                      </span>
                    </button>
                  ))}
                </div>
              </Disclosure.Panel>
            </>
          )}
        </Disclosure>
        <div className="h-[1px] bg-[#DEE0E3] w-full my-5" />
        <Disclosure defaultOpen={!isMobile && selectedDomains !== ""}>
          {({ open }) => (
            <>
              <Disclosure.Button
                className={`flex w-full justify-between text-base text-[#222F2B]`}
              >
                <span>{filterLabels["domains"]}</span>
                {open ? (
                  <Icon size={24} name="chevron-up" />
                ) : (
                  <Icon size={24} name="chevron-down" />
                )}
              </Disclosure.Button>
              <Disclosure.Panel className="pt-4 flex-col flex items-start">
                <input
                  onChange={(e) => handleSearchDomains(e.target.value)}
                  className="h-[35px] w-full py-2 px-3 rounded-md border border-[#DEE0E3] mb-4 placeholder-[#364B4480]"
                  placeholder="Search"
                />
                {searchResultDomains.map((option, optionIdx) => {
                  const isSelected = selectedDomains
                    .split(",")
                    .find((item) => item === option.value);
                  return (
                    <button
                      onClick={() => handleChangeDomains(option.value)}
                      key={optionIdx}
                      className="mb-3 flex flex-row items-center"
                    >
                      <img
                        className={`w-4 h-4 mr-3 rounded-sm ${
                          isSelected ? "bg-[#0A6DC2]" : ""
                        }`}
                        alt="checked"
                        src={
                          isSelected
                            ? "/icons/checked.svg"
                            : "/icons/unchecked.svg"
                        }
                      />
                      <span className="text-[#364B44] text-left">
                        {option.label}
                      </span>
                    </button>
                  );
                })}
              </Disclosure.Panel>
            </>
          )}
        </Disclosure>
        <div className="h-40 sm:h-32" />
        <div className="fixed bottom-0 left-0 right-0 bg-white flex flex-col-reverse sm:flex-row justify-between py-[26px] sm:py-8 px-[21px] sm:px-8">
          <button
            onClick={handleReset}
            className="w-full sm:w-[92px] h-11 sm:h-10 rounded-[90px] items-center justify-center text-[#292B2F] z-10"
          >
            <span>{filterLabels["reset-filters"]}</span>
          </button>
          <button
            onClick={handleApply}
            className="w-full sm:w-[92px] h-11 sm:h-10 rounded-[90px] items-center justify-center bg-[#0A6DC2] text-white mb-3 z-10"
          >
            <span>{filterLabels["apply"]}</span>
          </button>
        </div>
      </div>
    </Drawer>
  );
}

export default FilterDrawer;

export const optionsStudyTypes = [
  {
    value: "meta",
    elementTag: <MetaAnalysisTag pressable key="meta_analysis" />,
    label: "Meta-Analysis",
  },
  {
    value: "systematic",
    elementTag: <SystematicReviewTag pressable key="systemic_review" />,
    label: "Systematic Review",
  },
  {
    value: "rct",
    elementTag: <RctTag pressable key="rct" />,
    label: "RCT",
  },
  {
    value: "non_rct",
    elementTag: <NonRctTrialTag pressable key="non_rct" />,
    label: "Non-RCT Trial",
  },
  {
    value: "observational",
    elementTag: <ObservationalStudyTag pressable key="observational" />,
    label: "Observational",
  },
  {
    value: "lit_review",
    elementTag: <LiteratureReviewTag pressable key="lit_review" />,
    label: "Literature Review",
  },
  {
    value: "case",
    elementTag: <CaseStudyTag pressable key="case_study" />,
    label: "Case Report",
  },
  {
    value: "animal",
    elementTag: <AnimalTrialTag pressable key="animal" />,
    label: "Animal Trial",
  },
  {
    value: "in_vitro",
    elementTag: <InVitroTrialTag pressable key="in_vitro" />,
    label: "In-Vitro Trial",
  },
];

export const optionsDomain = [
  {
    value: "agri",
    label: "Agricultural and Food Sciences",
  },
  {
    value: "art",
    label: "Art",
  },
  {
    value: "bio",
    label: "Biology",
  },
  {
    value: "bus",
    label: "Business",
  },
  {
    value: "chem",
    label: "Chemistry",
  },
  {
    value: "cs",
    label: "Computer Science",
  },
  {
    value: "econ",
    label: "Economics",
  },
  {
    value: "edu",
    label: "Education",
  },
  {
    value: "eng",
    label: "Engineering",
  },
  {
    value: "env",
    label: "Environmental Science",
  },
  {
    value: "geog",
    label: "Geography",
  },
  {
    value: "geol",
    label: "Geology",
  },
  {
    value: "hist",
    label: "History",
  },
  {
    value: "law",
    label: "Law",
  },
  {
    value: "ling",
    label: "Linguistics",
  },
  {
    value: "mat",
    label: "Materials Science",
  },
  {
    value: "math",
    label: "Mathematics",
  },
  {
    value: "med",
    label: "Medicine",
  },
  {
    value: "philo",
    label: "Philosophy",
  },
  {
    value: "phys",
    label: "Physics",
  },
  {
    value: "poli",
    label: "Political Science",
  },
  {
    value: "psych",
    label: "Psychology",
  },
  {
    value: "soc",
    label: "Sociology",
  },
];
