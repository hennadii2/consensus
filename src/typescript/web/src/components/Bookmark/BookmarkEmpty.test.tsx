import { screen } from "@testing-library/react";
import { renderWithProviders } from "../../__tests__/renderWithProvider";
import BookmarkEmpty from "./BookmarkEmpty";

describe("components/BookmarkEmpty", () => {
  it("should render BookmarkEmpty", () => {
    renderWithProviders(<BookmarkEmpty />);

    const titleElement: HTMLElement = screen.getByTestId("title");
    expect(titleElement).toHaveTextContent("You did not save anything yet");

    const element2: HTMLElement = screen.getByTestId("try-searching");
    expect(element2).toHaveTextContent("Try searching:");

    expect(screen.queryByTestId("query-link")).toBeInTheDocument();
  });
});
