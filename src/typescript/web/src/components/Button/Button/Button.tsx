import classNames from "classnames";
import React, { ReactNode } from "react";

type Props = {
  className?: string;
  isLoading?: boolean;
  type?: "submit" | "button" | "reset";
  variant?: "primary" | "secondary";
  children: ReactNode;
  [rest: string]: any;
};

/**
 * @component Button
 * @description to use the hover effect the user needs to add the classname of the color. bg-{color}-{number}
 * e.g: bg-blue-700
 * @component
 * @example
 * return (
 *   <Button className="bg-green-600">Learn more</Button>
 * )
 */
const Button = ({
  className = "",
  type = "button",
  isLoading,
  children,
  variant,
  ...rest
}: Props) => {
  let defaultClassNames = [];

  if (variant === "primary") {
    defaultClassNames.push(
      "text-base bg-blue-300 text-blue-600 flex items-center gap-x-2 py-2 md:py-3 px-4 md:px-6 rounded-full"
    );
  } else if (variant === "secondary") {
    defaultClassNames.push(
      "text-base bg-[#0A6DC2] text-white flex items-center gap-x-2 py-2 md:py-3 px-4 md:px-6 rounded-full"
    );
  } else {
    if (!className.includes("rounded-")) {
      defaultClassNames.push("rounded-lg");
    }

    if (!className.includes("bg-opacity-")) {
      defaultClassNames.push("bg-opacity-80");
      defaultClassNames.push("hover:bg-opacity-100");
    }
  }

  return (
    <button
      {...rest}
      type={type}
      disabled={isLoading}
      className={classNames(
        "transition",
        className,
        defaultClassNames.join(" ")
      )}
    >
      {children}
      {isLoading ? <span className="loading-dot">...</span> : ""}
    </button>
  );
};

export default Button;
