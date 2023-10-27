import {
  claimDetailPagePath,
  getSearchTextFromResultUrl,
  resultsPagePath,
  searchPagePath,
} from "./pageUrl";

const WEB_URL = "https://consensus.com";
describe("helper/pageUrl", () => {
  process.env.NEXT_PUBLIC_WEBSITE_URL = WEB_URL;

  it("should valid searchPagePath", () => {
    expect(searchPagePath()).toMatch("/search/");
  });

  it("should valid resultsPagePath", () => {
    expect(resultsPagePath("Hello")).toMatch("/results/?q=Hello");
  });

  it("should valid resultsPagePath params", () => {
    expect(resultsPagePath("Hello", { yearMin: "2022" })).toMatch(
      "/results/?q=Hello&year_min=2022"
    );
    expect(
      resultsPagePath("Hello", {
        yearMin: "2020",
        yearMax: "2023",
        studyTypes: "rct,meta",
      })
    ).toMatch(
      "/results/?q=Hello&study_types=rct,meta&year_min=2020&year_max=2023"
    );
    expect(
      resultsPagePath("Hello", {
        fieldsOfStudy: "math,cs",
      })
    ).toMatch("/results/?q=Hello&domain=math,cs");
    expect(
      resultsPagePath("Hello", { sampleSizeMin: "100", sampleSizeMax: "200" })
    ).toMatch("/results/?q=Hello&sample_size_min=100&sample_size_max=200");
    expect(
      resultsPagePath("Hello", {
        sjrBestQuartileMin: "1",
        sjrBestQuartileMax: "3",
      })
    ).toMatch("/results/?q=Hello&sjr_min=1&sjr_max=3");
    expect(
      resultsPagePath("Hello", {
        filterControlledStudies: "true",
        filterHumanStudies: "true",
      })
    ).toMatch("/results/?q=Hello&controlled=true&human=true");
  });

  it("should valid claimDetailPagePath", () => {
    expect(claimDetailPagePath("slug", "id")).toMatch("/details/slug/id");
  });

  it("should valid getSearchTextFromResultUrl", () => {
    expect(
      getSearchTextFromResultUrl(
        "http://localhost:3000/results/?q=do%20direct%20cash%20transfers%20reduce%20poverty%3F&synthesize=on&year_min=1990&study_types=meta,systematic,rct,case"
      )
    ).toMatch(
      "do direct cash transfers reduce poverty? - 1990-now, Meta-Analysis, Systematic Review, RCT, Case Report"
    );
    expect(
      getSearchTextFromResultUrl(
        "https://staging.consensus.app/results/?q=do%20direct%20cash%20transfers%20reduce%20poverty%3F&synthesize=on&year_min=1990"
      )
    ).toMatch("do direct cash transfers reduce poverty? - 1990-now");
    expect(
      getSearchTextFromResultUrl(
        "https://staging.consensus.app/results/?q=do%20direct%20cash%20transfers%20reduce%20poverty%3F&synthesize=on&study_types=meta,systematic"
      )
    ).toMatch(
      "do direct cash transfers reduce poverty? - Meta-Analysis, Systematic Review"
    );
  });
});
