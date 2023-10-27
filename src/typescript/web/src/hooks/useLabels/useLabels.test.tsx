import LABELS from "constants/labels.json";
import useLabels from "hooks/useLabels";
import init from "jooks";

describe("hooks/useLabels", () => {
  let args = "";
  const jooks = init(() => useLabels(args));

  it("should return the correct page-title", () => {
    args = "page-title";
    const [pageTitle] = jooks.run();

    expect(pageTitle).toBe(LABELS["page-title"]);
  });

  it("should return the correct json: general", () => {
    args = "general";
    const [generalLabels] = jooks.run();

    expect(generalLabels).toBe(LABELS.general);
  });

  it("should return the correct json: screens", () => {
    args = "screens";
    const [screensLabels] = jooks.run();

    expect(screensLabels).toBe(LABELS.screens);
  });
});
