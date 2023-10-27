import { render, screen } from "@testing-library/react";
import { ScoreTooltip } from "components/Tooltip";
import LABELS from "constants/labels.json";

describe("components/ScoreTooltip", () => {
  it("should render score tooltip", () => {
    render(<ScoreTooltip />);

    const scoreTooltip = screen.getByTestId("tooltip-score");

    expect(scoreTooltip).toBeInTheDocument();
  });

  it("should have a content", () => {
    render(<ScoreTooltip />);

    const title = screen.getByText(LABELS.tooltips.score.title);
    const content = screen.getByText(LABELS.tooltips.score.content);

    expect(title).toBeInTheDocument();
    expect(content).toBeInTheDocument();
  });
});
