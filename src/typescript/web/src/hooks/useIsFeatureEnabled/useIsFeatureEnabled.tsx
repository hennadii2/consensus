import { FeatureFlag, ForceEnabledFeatures } from "enums/feature-flag";
import { useEffect, useState } from "react";
import { getCookie } from "react-use-cookie";

/**
 * @hook useIsFeatureEnabled
 * @description Hook for checking if the feature is enabled (for testing only)
 * @example
 * const isClaimScoreEnabled = useIsFeatureEnabled('claim-score');
 */
const useIsFeatureEnabled = (feature: FeatureFlag, ...args: any[]) => {
  const enabledFeatures = getCookie("features").split(" ");
  const [isEnabled, setIsEnabled] = useState<boolean>(false);

  // need to use this because of the elements are rendered in client-side
  useEffect(() => {
    const isEnabled =
      enabledFeatures.includes(feature) ||
      ForceEnabledFeatures.includes(feature);
    setIsEnabled(isEnabled);
  }, [enabledFeatures, feature]);

  // trick to make the hook testable
  if (args[0] === "testing") return enabledFeatures.includes(feature);

  return isEnabled;
};

export default useIsFeatureEnabled;
