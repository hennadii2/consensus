import { FeatureFlag } from "enums/feature-flag";
import { setCookie } from "react-use-cookie";

export default function addFeature(
  cookieFeatures: string,
  feature: FeatureFlag
): boolean {
  const splittedFeatures = cookieFeatures.split(" ");
  if (splittedFeatures.includes(feature) == false) {
    setCookie(
      "features",
      cookieFeatures == "" ? feature : cookieFeatures + " " + feature
    );
    return true;
  }
  return false;
}

export function removeFeature(
  cookieFeatures: string,
  feature: FeatureFlag
): boolean {
  const splittedFeatures = cookieFeatures.split(" ");
  if (splittedFeatures.includes(feature)) {
    setCookie(
      "features",
      splittedFeatures.filter((featureArg) => featureArg !== feature).join(" ")
    );
    return true;
  }
  return false;
}
