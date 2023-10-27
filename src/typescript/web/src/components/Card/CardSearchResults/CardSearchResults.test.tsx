import { screen } from "@testing-library/react";
import { renderWithProviders } from "../../../__tests__/renderWithProvider";
import CardSearchResults from "./CardSearchResults";

describe("components/Card/CardSearchResults", () => {
  it("should render CardSearchResults", () => {
    renderWithProviders(<CardSearchResults items={[]} />);

    const div: HTMLDivElement = screen.getByTestId("card-search-results");

    expect(div).toBeInTheDocument();
  });
});
