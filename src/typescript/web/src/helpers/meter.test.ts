import { meterSummary } from "./meter";

describe("helper/meter", () => {
  it("should return valid meterSummary", () => {
    expect(meterSummary({ YES: 50, POSSIBLY: 0, NO: 40 })).toStrictEqual({
      answer: "YES",
      percent: 50,
    });
  });

  it("should return mixed", () => {
    expect(meterSummary()).toStrictEqual({ answer: "MIXED", percent: 0 });
    expect(meterSummary({ YES: 50, POSSIBLY: 0, NO: 50 })).toStrictEqual({
      answer: "MIXED",
      percent: 50,
    });
  });

  it("should return mixed yes", () => {
    expect(meterSummary({ YES: 50, POSSIBLY: 50, NO: 0 })).toStrictEqual({
      answer: "MIXED_YES",
      percent: 50,
    });
  });

  it("should return mixed no", () => {
    expect(meterSummary({ YES: 0, POSSIBLY: 50, NO: 50 })).toStrictEqual({
      answer: "MIXED_NO",
      percent: 50,
    });
  });
});
