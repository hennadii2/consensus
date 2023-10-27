import Button from "components/Button";
import Icon from "components/Icon";
import useLabels from "hooks/useLabels";
import React from "react";

/**
 * @component ScoreTooltip
 * @description Tooltip for score
 * @example
 * return (
 *   <ScoreTooltip />
 * )
 */
const ScoreTooltip = () => {
  const [generalLabels, componentLabels] = useLabels(
    "general",
    "tooltips.score"
  );
  return (
    <div className="pr-4" data-testid="tooltip-score">
      <p className="font-bold mb-3">{componentLabels.title}</p>
      <p className="mb-4">{componentLabels.content}</p>
      <Button className="bg-gray-300 px-4 py-1.5 flex items-center">
        {generalLabels["learn-more"]}
        <Icon name="external-link" size={16} className="ml-2" />
      </Button>
    </div>
  );
};

export default ScoreTooltip;
