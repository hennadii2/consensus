/**
 * @hook useBadgeScore
 * @description Hook for getting text and text color. return depends on score
 * @example
 * const { resultText, resultColor } = useBadgeScore(9);
 */

import useLabels from "hooks/useLabels";

const useBadgeScore = (score: number) => {
  const [generalLabels] = useLabels("general");

  if (score >= 9) {
    return {
      resultText: generalLabels.best,
      resultColor: "green-700",
    };
  } else if (score >= 8) {
    return {
      resultText: generalLabels.great,
      resultColor: "green-600",
    };
  }

  return {
    resultText: generalLabels.good,
    resultColor: "green-300",
  };
};

export default useBadgeScore;
