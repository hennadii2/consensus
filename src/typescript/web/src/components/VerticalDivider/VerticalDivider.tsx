import React from "react";

type VerticalDividerProps = {
  height?: number;
  width?: number;
};

/**
 * @component VerticalDivider
 * @description Divider component for separating two values
 * @example
 * return (<VerticalDivider />)
 */
const VerticalDivider = ({ height = 17, width = 1 }: VerticalDividerProps) => {
  return (
    <div
      className="bg-gray-200"
      style={{ height, width }}
      data-testid="vertical-divider"
    />
  );
};

export default VerticalDivider;
