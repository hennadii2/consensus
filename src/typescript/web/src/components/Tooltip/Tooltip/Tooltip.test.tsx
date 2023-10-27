import { fireEvent, screen } from "@testing-library/react";
import Tooltip, { ScoreTooltip } from "components/Tooltip";
import LABELS from "constants/labels.json";
import { renderWithProviders } from "../../../__tests__/renderWithProvider";

describe("components/Tooltip", () => {
  it("should render tooltip", () => {
    renderWithProviders(
      <Tooltip tooltipContent={<ScoreTooltip />}>
        <p>Score</p>
      </Tooltip>
    );

    const tooltip = screen.getByTestId("tooltip");

    expect(tooltip).toBeInTheDocument();
  });

  it("should show tooltip content", () => {
    renderWithProviders(
      <Tooltip tooltipContent={<ScoreTooltip />}>
        <p>Score</p>
      </Tooltip>
    );

    const tooltipText = screen.getByText("Score");
    fireEvent.mouseEnter(tooltipText, {
      bubbles: true,
    });

    const title = screen.getByText(LABELS.tooltips.score.title);
    const content = screen.getByText(LABELS.tooltips.score.content);

    expect(title).toBeInTheDocument();
    expect(content).toBeInTheDocument();
  });
});
