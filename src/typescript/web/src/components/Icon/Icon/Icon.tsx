import classNames from "classnames";
import startCase from "lodash/startCase";
import React from "react";
import * as FeatherIcons from "react-feather";

type IconProps = {
  name: string;
  size?: number;
  color?: string;
  className?: string | null;
  [rest: string]: any;
};

/**
 * @component Icon
 * @description Component for react-feather icon. This can be change to something else someday
 * @link https://feathericons.com/
 * @example
 * return (
 *   <Icon name="search" />
 * )
 */
const Icon = function ({
  name = "",
  size = 24,
  color = "#000000",
  className = null,
  ...rest
}: IconProps) {
  if (!name) {
    throw new Error("Name property is required");
  }

  const parsedName = name.split("-").map(startCase).join("").replace(/ /g, "");
  const Component = (FeatherIcons as any)[parsedName];

  if (!Component) {
    throw new Error(
      "Icon not found. Please visit this site https://feathericons.com/ for reference."
    );
  }

  return (
    <Component
      data-testid="icon"
      {...rest}
      className={classNames(className, "stroke-current")}
      size={size}
      color={color}
    />
  );
};

export default Icon;
