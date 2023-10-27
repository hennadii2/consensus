import FeatureFlagItem from "components/FeatureFlagItem";
import { FeatureFlagOptions } from "enums/feature-flag";
import useLabels from "hooks/useLabels";
import type { NextPage } from "next";
import { ChangeEvent, useEffect, useMemo } from "react";
import useCookie, { getCookie } from "react-use-cookie";

/**
 * @page FeatureFlag
 * @description Feature flag page. Page controls the next version components
 */

interface FEATURE_FLAG_ITEM {
  label: string;
  name: string;
}

const FeatureFlag: NextPage = () => {
  const [features, setFeatures] = useCookie("features", "");
  const [pageLabels] = useLabels("screens.feature-flag");

  useEffect(() => {
    setFeatures(getCookie("features"));
  }, [setFeatures]);

  const splittedFeatures = useMemo(() => {
    return features.split(" ");
  }, [features]);

  const onCheckboxChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { checked, name } = e.target;

    setFeatures(
      checked
        ? `${features} ${name}`
        : splittedFeatures.filter((feature) => feature !== name).join(" ")
    );
  };

  return (
    <div className="container py-10">
      <p className="text-black text-2xl font-bold mb-6">{pageLabels.title}</p>
      {(FeatureFlagOptions as FEATURE_FLAG_ITEM[]).map((item) => (
        <FeatureFlagItem
          key={item.name}
          name={item.name}
          features={splittedFeatures}
          onChange={onCheckboxChange}
        >
          {item.label}
        </FeatureFlagItem>
      ))}
    </div>
  );
};

export default FeatureFlag;
