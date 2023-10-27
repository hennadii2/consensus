import { Badges, StudyDetailsResponse } from "./api";
import { isStudySnapshotEmpty } from "./studyDetail";

describe("helper/studyDetail", () => {
  it("should return true", () => {
    const studyDetail: StudyDetailsResponse = {
      population: null,
      method: null,
      outcome: null,
      dailyLimitReached: false,
    };

    const badges: Badges = {
      very_rigorous_journal: false,
      rigorous_journal: false,
      highly_cited_paper: false,
      study_type: undefined,
      sample_size: undefined,
      study_count: undefined,
      animal_trial: undefined,
      large_human_trial: undefined,
      disputed: undefined,
      enhanced: false,
    };

    expect(isStudySnapshotEmpty(studyDetail, badges)).toEqual(true);
  });

  it("should return false", () => {
    const studyDetail: StudyDetailsResponse = {
      population: null,
      method: null,
      outcome: null,
      dailyLimitReached: false,
    };

    const badges: Badges = {
      very_rigorous_journal: false,
      rigorous_journal: false,
      highly_cited_paper: false,
      study_type: undefined,
      sample_size: undefined,
      study_count: 100,
      animal_trial: undefined,
      large_human_trial: undefined,
      disputed: undefined,
      enhanced: false,
    };

    expect(isStudySnapshotEmpty(studyDetail, badges)).toEqual(false);
  });

  it("should return false", () => {
    const studyDetail: StudyDetailsResponse = {
      population: "population",
      method: null,
      outcome: null,
      dailyLimitReached: false,
    };

    const badges: Badges = {
      very_rigorous_journal: false,
      rigorous_journal: false,
      highly_cited_paper: false,
      study_type: undefined,
      sample_size: undefined,
      study_count: undefined,
      animal_trial: undefined,
      large_human_trial: undefined,
      disputed: undefined,
      enhanced: false,
    };

    expect(isStudySnapshotEmpty(studyDetail, badges)).toEqual(false);
  });
});
