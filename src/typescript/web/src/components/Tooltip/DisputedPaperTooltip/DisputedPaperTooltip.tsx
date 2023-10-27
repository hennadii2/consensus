import Button from "components/Button";
import Icon from "components/Icon";
import React from "react";

interface DisputedPaperTooltipProps {
  title: string;
  content: string;
  icon: string;
  buttonUrl: string;
  buttonText: string;
}

/**
 * @component DisputedPaperTooltip
 * @description Tooltip for the disputed paper badge
 * @example
 * return (
 *   <DisputedPaperTooltip />
 * )
 */
const DisputedPaperTooltip = ({
  title,
  icon,
  content,
  buttonText,
  buttonUrl,
}: DisputedPaperTooltipProps) => {
  const handleClick = (e: any) => {
    e.preventDefault();
    window.open(buttonUrl);
  };

  return (
    <div data-testid="tooltip-score">
      <p className="font-bold mb-3 text-lg flex items-center">
        <img className="w-6 mr-2" alt={title} src={icon} />
        {title}
      </p>
      <p
        className="text-base"
        dangerouslySetInnerHTML={{ __html: content }}
      ></p>
      <a
        onClick={handleClick}
        href={buttonUrl}
        target="__blank"
        rel="noreferrer"
      >
        <Button className="bg-gray-300 px-4 py-1.5 flex items-center rounded-full mt-4 text-[#000000]">
          {buttonText}
          <Icon name="external-link" size={16} className="ml-2" />
        </Button>
      </a>
    </div>
  );
};

export default DisputedPaperTooltip;
