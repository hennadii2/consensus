import { getDaysBetweenDates, getMinutesBetweenDates } from "./date";

describe("helper/date", () => {
  it("sould valid getDaysBetweenDates", () => {
    expect(getDaysBetweenDates(new Date(), new Date())).toBe(0);
    expect(
      getDaysBetweenDates(
        new Date("2022-08-11T19:47:27.311Z"),
        new Date("2022-08-18T19:47:27.311Z")
      )
    ).toBe(7);
  });

  it("sould valid getMinutesBetweenDates", () => {
    expect(getMinutesBetweenDates(new Date(), new Date())).toBe(0);
    expect(
      getMinutesBetweenDates(
        new Date("2022-08-11T19:47:27.311Z"),
        new Date("2022-08-11T20:47:27.311Z")
      )
    ).toBe(60);
  });
});
