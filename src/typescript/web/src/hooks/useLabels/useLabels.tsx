import LABELS from "constants/labels.json";
import get from "lodash/get";
import { useMemo } from "react";

type UseLabelsProps = string[];

/**
 * @hook useLabels
 * @description returns array which consists of json data of labels depending on the arguments
 * @example
 * const [generalLabels, homepageLabels] = useLabels('general', 'screens.index');
 */
const useLabels = (...args: UseLabelsProps) => {
  const labels = LABELS as any;

  return useMemo(() => {
    if (!args.length) {
      return labels;
    }

    return args.reduce((accumulator: any[], currentValue) => {
      return [...accumulator, get(labels, currentValue)];
    }, []);
  }, [args, labels]);
};

export default useLabels;
