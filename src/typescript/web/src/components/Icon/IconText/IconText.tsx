import React from "react";

export type IconTextProps = {
  icon: string;
  title: string;
  items: string[];
  align?: string;
  onClickItem?: (item: string) => void;
};

/**
 * @component IconText
 * @description Component for icon with text
 * @example
 * return (
 *   <IconText icon="icon" text="this is a text" items={["hello"]} />
 * )
 */
const IconText = ({
  icon,
  title,
  items,
  align,
  onClickItem,
}: IconTextProps) => {
  return (
    <div
      className="bg-white rounded-3xl px-7 py-10 shadow-card w-full h-full"
      data-testid="icon-text"
    >
      <div style={{ justifyContent: align }} className="flex">
        <div className="h-[80px] w-[80px] bg-[#ECF6FE] rounded-xl flex items-center justify-center">
          <img src={`/icons/search/${icon}.svg`} alt={title} />
        </div>
      </div>
      <div style={{ alignItems: align }} className="flex flex-col">
        <h2
          style={{ textAlign: align as any }}
          className="font-bold text-xl mt-5"
        >
          {title}
        </h2>
        {items?.map((item) => (
          <a
            key={item}
            data-testid="icon-text-item"
            href={`/results?q=${item}`}
            onClick={(event) => {
              event.preventDefault();
              onClickItem?.(item);
            }}
            className="text-sm text-gray-600 mt-3 cursor-pointer border border-[#E4E9EC] rounded-full px-4 py-1 w-fit hover:shadow-card transition"
          >
            {item}
          </a>
        ))}
      </div>
    </div>
  );
};

export default IconText;
