import React from "react";

type Props = {
  onClick?: () => void;
  className?: string;
  isActiveFilter?: boolean;
};

/**
 * @component FilterButton
 * @description designed for filter button
 * @example
 * return (
 *   <FilterButton onClick={fn}></FilterButton>
 * )
 */
const FilterButton = ({ onClick, className, isActiveFilter }: Props) => {
  return (
    <button
      onClick={onClick}
      data-testid="filter-button"
      className={`text-base bg-white flex items-center justify-center w-[44px] md:w-auto px-0 md:px-3 h-[44px] gap-x-4 md:gap-x-[10px] rounded-full border border-[#DEE0E3] hover:shadow-[0_2px_4px_0_rgba(189,201,219,0.32)] ${
        isActiveFilter ? "border border-[#0A6DC2]" : ""
      } ${className}`}
    >
      <img
        alt="filter"
        src={isActiveFilter ? "/icons/filter2.svg" : "/icons/filter.svg"}
        className="w-5 h-5"
      />
      <span className="hidden md:block whitespace-nowrap text-[#222F2B] text-base">
        Filter
      </span>
    </button>
  );
};

export default FilterButton;
