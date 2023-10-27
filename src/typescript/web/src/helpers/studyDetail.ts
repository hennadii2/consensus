import { Badges, StudyDetailsResponse } from "./api";

export function isStudySnapshotEmpty(
  studyDetail: StudyDetailsResponse,
  badges?: Badges
): boolean {
  if (
    (studyDetail.method == null ||
      studyDetail.method == "" ||
      studyDetail.method == "n/a") &&
    (studyDetail.outcome == null ||
      studyDetail.outcome == "" ||
      studyDetail.outcome == "n/a") &&
    (studyDetail.population == null ||
      studyDetail.population == "" ||
      studyDetail.population == "n/a")
  ) {
    if (!badges || (!badges.sample_size && !badges.study_count)) {
      return true;
    }
  }

  return false;
}
