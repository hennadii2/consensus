import { screen } from "@testing-library/react";
import BetaTag from "components/BetaTag";
import { renderWithProviders } from "../../__tests__/renderWithProvider";

describe("components/Tag", () => {
  it("should render beta tag", () => {
    renderWithProviders(<BetaTag />);

    const tag: HTMLAnchorElement = screen.getByTestId("beta-tag");

    expect(tag).toBeInTheDocument();
  });

  it("should render beta tag with text", () => {
    renderWithProviders(<BetaTag text />);

    const tag: HTMLAnchorElement = screen.getByTestId("beta-tag-text");

    expect(tag).toBeInTheDocument();
  });
});
