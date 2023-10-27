export enum FeatureFlag {
  TEST_FEATURE = "test-feature",
  BOOKMARK = "bookmark",
  RELEVANCY_LABELS = "relevancy-labels",
  PAPER_SEARCH = "paper-search",
  STUDY_SNAPSHOT = "study-snapshot",
}

export const FeatureFlagOptions = [
  {
    label: "Bookmark",
    name: FeatureFlag.BOOKMARK,
  },
  {
    label: "Relevancy Labels",
    name: FeatureFlag.RELEVANCY_LABELS,
  },
  {
    label: "Paper Search",
    name: FeatureFlag.PAPER_SEARCH,
  },
  {
    label: "Study Snapshot",
    name: FeatureFlag.STUDY_SNAPSHOT,
  },
];

/** Features that are enabled by default. */
export const ForceEnabledFeatures: FeatureFlag[] = [
  FeatureFlag.BOOKMARK,
  FeatureFlag.RELEVANCY_LABELS,
  FeatureFlag.STUDY_SNAPSHOT,
];
