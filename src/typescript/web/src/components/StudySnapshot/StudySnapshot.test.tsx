import { screen } from "@testing-library/react";
import { renderWithProviders } from "../../__tests__/renderWithProvider";
import StudySnapshot from "./StudySnapshot";

describe("components/StudySnapshot/StudySnapshot", () => {
  it("should render StudySnapshot(Collapsed)", () => {
    renderWithProviders(<StudySnapshot paperId="270" isDetailPage={false} />);

    const headerButton: HTMLElement = screen.getByTestId(
      "snapshot-header-button"
    );
    expect(headerButton).toBeInTheDocument();

    expect(
      screen.queryByTestId("snapshot-expanded-widget")
    ).not.toBeInTheDocument();
  });
});
