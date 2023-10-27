import { FeatureFlag, ForceEnabledFeatures } from "enums/feature-flag";
import qs from "querystring";

export default function getFeatureEnabled(
  cookie: string,
  feature: FeatureFlag
): boolean {
  const cookies = qs.decode(cookie, "; ");

  const enabledFeatures = (cookies?.features as string)?.split(" ") || [];

  return (
    enabledFeatures.includes(feature) || ForceEnabledFeatures.includes(feature)
  );
}
