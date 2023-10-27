import useBadgeScore from "hooks/useBadgeScore";
import init from "jooks";

describe("hooks/useBadgeScore", () => {
  let num = 0;
  const jooks = init(() => useBadgeScore(num));

  it("should return the text: Best and color: green-700", () => {
    num = 9;
    const { resultText, resultColor } = jooks.run();

    expect(resultText).toBe("Best");
    expect(resultColor).toBe("green-700");
  });

  it("should return the text: Great and color: green-600", () => {
    num = 8;
    const { resultText, resultColor } = jooks.run();

    expect(resultText).toBe("Great");
    expect(resultColor).toBe("green-600");
  });

  it("should return the text: Great and color: green-600", () => {
    num = 5;
    const { resultText, resultColor } = jooks.run();

    expect(resultText).toBe("Good");
    expect(resultColor).toBe("green-300");
  });
});
