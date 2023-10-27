import { FeatureFlag } from "enums/feature-flag";
import init from "jooks";
import useIsFeatureEnabled from "./useIsFeatureEnabled";

describe("hooks/useIsFeatureEnabled", () => {
  let feature = FeatureFlag.TEST_FEATURE;
  const jooks = init(() => useIsFeatureEnabled(feature, "testing"));

  it("should return true", async () => {
    Object.defineProperty(document, "cookie", {
      writable: true,
      value: `features=${FeatureFlag.TEST_FEATURE}`,
    });
    feature = FeatureFlag.TEST_FEATURE;
    const isEnabled = jooks.run();
    expect(isEnabled).toBeTruthy();
  });

  it("should return false", async () => {
    Object.defineProperty(document, "cookie", {
      writable: true,
      value: `features=`,
    });
    feature = FeatureFlag.TEST_FEATURE;
    const isEnabled = jooks.run();
    expect(isEnabled).toBeFalsy();
  });
});
