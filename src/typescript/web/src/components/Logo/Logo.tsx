import BetaTag from "components/BetaTag";
import React, { useMemo } from "react";

type LogoProps = {
  size: "small" | "large" | "medium";
  hasBackground?: boolean;
  hasBeta?: boolean;
};

/**
 * @component Logo
 * @description Component for showing logo of the project.
 * @example
 * return (
 *   <Logo size="small" hasBackground />
 * )
 */
const Logo = ({ size, hasBackground = false, hasBeta }: LogoProps) => {
  const img = useMemo(() => {
    const name = size === "small" ? "logo-min.svg" : "logo-full.svg";
    return (
      <img
        className={
          size === "medium"
            ? "w-[156px]"
            : size === "small"
            ? "w-[26px] h-[26px]"
            : size === "large"
            ? "w-[180px] md:w-[250px]"
            : ""
        }
        data-testid="logo-img"
        src={`/images/${name}`}
        alt="logo"
      />
    );
  }, [size]);

  if (hasBackground) {
    return (
      <div
        data-testid="logo-bg"
        className="bg-white rounded-lg w-10 h-10 p-[7px]"
      >
        {img}
      </div>
    );
  }

  return (
    <div className="relative">
      {img}
      {hasBeta && (
        <div className="absolute bottom-2 md:bottom-4 right-2">
          <BetaTag />
        </div>
      )}
    </div>
  );
};

export default Logo;
