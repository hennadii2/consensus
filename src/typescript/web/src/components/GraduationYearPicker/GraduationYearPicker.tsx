import { Listbox, Transition } from "@headlessui/react";
import Icon from "components/Icon";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import { Fragment, useEffect, useMemo, useState } from "react";

interface GraduationYearPicker {
  value?: string;
  onChange: (value: string) => void;
}

/**
 * @component GraduationYearPicker
 * @description component for graduation year picker
 * @example
 * return (
 *   <GraduationYearPicker />
 * )
 */
export default function GraduationYearPicker({
  value,
  onChange,
}: GraduationYearPicker) {
  const [yearPickerLabels] = useLabels(
    "student-discount.ask-graduation-year-modal.year-picker"
  );
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  const [selected, setSelected] = useState(value || yearPickerLabels["year"]);

  const options = useMemo(() => {
    const thisYear = new Date().getFullYear();
    const years = [
      (thisYear + 1).toString(),
      (thisYear + 2).toString(),
      (thisYear + 3).toString(),
      (thisYear + 4).toString() + "+",
    ];
    return years;
  }, []);

  useEffect(() => {
    setSelected(value || yearPickerLabels["year"]);
  }, [value, yearPickerLabels]);

  const handleChange = (value: string) => {
    onChange(value);
    setSelected(value);
  };

  const isActive = selected !== yearPickerLabels["year"];

  return (
    <div
      data-testid="graduation-year-picker"
      style={{
        boxShadow: "-4px 6px 25px 0px rgba(189, 201, 219, 0.20)",
      }}
    >
      <Listbox value={selected} onChange={handleChange}>
        {({ open }) => (
          <div className="relative">
            <Listbox.Button
              className={`flex items-center gap-2 relative h-[56px] w-full justify-between cursor-pointer rounded-[12px] bg-white px-5 text-left focus:outline-none text-base ${
                open ? "rounded-b-none" : ""
              }`}
            >
              <span className="whitespace-nowrap block text-[#222F2B]">
                {selected}
              </span>
              <div
                className="block"
                style={{
                  transform: open ? "rotate(180deg)" : "rotate(0deg)",
                  transition: "0.3s",
                }}
              >
                <Icon
                  name="chevron-down"
                  size={20}
                  className="text-[#222F2B]"
                />
              </div>
            </Listbox.Button>
            <Transition
              as={Fragment}
              leave="transition ease-in duration-100"
              leaveFrom="opacity-100"
              leaveTo="opacity-0"
            >
              <Listbox.Options className="relative z-10 min-w-[100px] w-full px-5 pb-5 rounded-b-[12px] bg-white text-base text-gray-700 focus:outline-none">
                <div className="overflow-auto border-t border-[#DEE0E3]">
                  {options.map((option, optionIdx) => (
                    <Listbox.Option
                      key={optionIdx}
                      className={({ active }) =>
                        `relative cursor-pointer select-none text-left ${
                          optionIdx === 0 ? "mt-2.5" : ""
                        }`
                      }
                      value={option}
                    >
                      {({ selected }) => (
                        <>
                          <span
                            className={`block truncate duration-100 px-5 py-2 rounded-full ${
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
                  ))}
                </div>
              </Listbox.Options>
            </Transition>
          </div>
        )}
      </Listbox>
    </div>
  );
}
