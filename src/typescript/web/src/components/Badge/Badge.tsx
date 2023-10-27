import classNames from "classnames";
import React, { ReactNode } from "react";

type BadgeProps = {
  children: ReactNode;
  className?: string;
  size?: "sm" | "md" | "lg";
};

/**
 * @component Badge
 * @description Component for badges. Text is wrapped in a container that can have a custom background
 * @example
 * return (
 *   <Badge className="bg-red-400">This is a badge</Badge>
 * )
 */
const Badge = ({
  children,
  className = "",
  size = "md",
  ...rest
}: BadgeProps) => {
  return (
    <div
      data-testid="badge"
      {...rest}
      className={classNames("rounded-xl text-center", className, {
        "px-2 py-1": size === "sm",
        "px-4 py-1": size === "md",
        "px-3 py-1.5": size === "lg",
      })}
    >
      {children}
    </div>
  );
};

export default Badge;
