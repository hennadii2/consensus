import parseSubText from "./parseSubText";

describe("helper/parseSubText", () => {
  it("should valid parse", () => {
    expect(parseSubText({ journal: "hello", year: 2022 })).toMatch(
      "Published in hello | 2022"
    );
  });
});
