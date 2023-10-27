import { screen } from "@testing-library/react";
import { renderWithProviders } from "../../__tests__/renderWithProvider";
import CreditTag from "./CreditTag";

describe("components/CreditTag", () => {
  it("should render credit tag", () => {
    renderWithProviders(<CreditTag />);

    const tag: HTMLAnchorElement = screen.getByTestId("credit-tag");

    expect(tag).toBeInTheDocument();
  });
});
