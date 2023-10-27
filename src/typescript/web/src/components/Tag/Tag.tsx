import React from "react";

type TagProps = {
  q?: string;
  children: React.ReactNode;
  onClick?: (event: React.MouseEvent) => void;
};

/**
 * @component Tag
 * @description Wrapper component to highlight a link or indicate a call to action.
 * @example
 * return (
 *   <Tag>This is a tag</Tag>
 * )
 */
const Tag = ({ q = "", onClick, children }: TagProps) => {
  let classNames =
    "text-green-600 font-normal bg-white rounded-full px-4 py-1 cursor-pointer transition hover:drop-shadow-tag bg-opacity-100";

  if (!q) {
    return (
      <div data-testid="tag" className={classNames} onClick={onClick}>
        {children}
      </div>
    );
  }

  return (
    <a
      href={`/results?q=${q}`}
      data-testid="tag"
      onClick={onClick}
      className={classNames}
    >
      {children}
    </a>
  );
};

export default Tag;
