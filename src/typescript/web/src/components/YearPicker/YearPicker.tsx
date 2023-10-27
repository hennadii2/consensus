import { Listbox, Transition } from "@headlessui/react";
import Icon from "components/Icon";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import { Fragment, useEffect, useMemo, useState } from "react";

interface YearPicker {
  value?: string;
  onChange: (value: string) => void;
}

/**
 * @component YearPicker
 * @description component for year picker
 * @example
 * return (
 *   <YearPicker />
 * )
 */
export default function YearPicker({ value, onChange }: YearPicker) {
  const [generalLabels] = useLabels("general");
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  const [selected, setSelected] = useState(value || generalLabels["all-years"]);

  const options = useMemo(() => {
    const years = ["2018", "2015", "2010", "2005", "2000", "1990"];

    // generate current year - 1
    const thisYear = new Date().getFullYear();
    for (let index = Number(years[0]) + 1; index <= thisYear; index++) {
      years.unshift(index.toString());
    }

    return years;
  }, []);

  useEffect(() => {
    setSelected(value || generalLabels["all-years"]);
  }, [value, generalLabels]);

  const handleChange = (value: string) => {
    onChange(value);
    setSelected(value);
  };

  const isActive = selected !== generalLabels["all-years"];

  return (
    <div data-testid="year-picker">
      <Listbox value={selected} onChange={handleChange}>
        {({ open }) => (
          <div className="relative">
            <Listbox.Button
              className={`flex items-center gap-2 relative w-[44px] md:w-max h-[44px] justify-center cursor-pointer rounded-full bg-white px-2.5 md:px-4 text-left focus:outline-none text-base ${
                isActive ? "border-[#085394]" : "border-[#DEE0E3]"
              } md:border-[#DEE0E3] border`}
            >
              <img
                src={
                  isMobile && isActive
                    ? "/icons/date-selected.svg"
                    : "/icons/date.svg"
                }
                alt="date icon"
              />
              <span className="whitespace-nowrap hidden md:block">
                {isActive ? `${generalLabels["since"]} :` : ""} {selected}
              </span>
              <div
                className="hidden md:block"
                style={{
                  transform: open ? "rotate(180deg)" : "rotate(0deg)",
                  transition: "0.3s",
                }}
              >
                <Icon name="chevron-down" size={20} />
              </div>
            </Listbox.Button>
            <Transition
              as={Fragment}
              leave="transition ease-in duration-100"
              leaveFrom="opacity-100"
              leaveTo="opacity-0"
            >
              <Listbox.Options className="absolute z-10 mt-1 min-w-[100px] w-full rounded-md bg-white py-1 text-base text-gray-700 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                <div className="text-center py-2 border-b border-b-gray-200">
                  {generalLabels["since"]}:
                </div>
                <div className="max-h-[15.5rem] overflow-auto">
                  {[generalLabels["all-years"], ...options].map(
                    (option, optionIdx) => (
                      <Listbox.Option
                        key={optionIdx}
                        className={({ active }) =>
                          `relative cursor-pointer select-none text-center px-4 ${
                            optionIdx === 0 ? "mt-2.5" : ""
                          }`
                        }
                        value={option}
                      >
                        {({ selected }) => (
                          <>
                            <span
                              className={`block truncate duration-100 py-2 rounded-full ${
                                selected
                                  ? "font-medium bg-[#EFFCF8] text-[#23B094]"
                                  : "font-normal"
                              }`}
                            >
                              {option}
                            </span>
                          </>
                        )}
                      </Listbox.Option>
                    )
                  )}
                </div>
              </Listbox.Options>
            </Transition>
          </div>
        )}
      </Listbox>
    </div>
  );
}
