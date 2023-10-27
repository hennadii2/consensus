import NextLink from "next/link";
import React from "react";

type LinkProps = {
  href?: string;
  children: React.ReactNode;
};

/**
 * @component Link
 * @description Wrapper component for next/link with blue colored text style
 * @example
 * return (
 *   <Link>This is a link</Link>
 * )
 */
const Link = ({ href = "/", children }: LinkProps) => {
  return (
    <NextLink href={href}>
      <a data-testid="blue-colored-link" className="text-blue-600 font-bold">
        {children}
      </a>
    </NextLink>
  );
};

export default Link;
