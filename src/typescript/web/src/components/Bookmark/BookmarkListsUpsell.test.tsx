import { screen } from "@testing-library/react";
import { renderWithProviders } from "./../../__tests__/renderWithProvider";
import BookmarkListsUpsell from "./BookmarkListsUpsell";

describe("components/BookmarkListsUpsell", () => {
  it("should render BookmarkListsUpsell(Free)", () => {
    renderWithProviders(<BookmarkListsUpsell isPremium={false} />);

    const title1Element: HTMLElement = screen.getByTestId("title1");
    expect(title1Element).toHaveTextContent("Want unlimited?");

    const title2Element: HTMLElement = screen.getByTestId("title2");
    expect(title2Element).toHaveTextContent("Upgrade to Premium");

    const listsLeftTextElement: HTMLElement =
      screen.getByTestId("lists-left-text");
    expect(listsLeftTextElement).toHaveTextContent("Custom Lists left");

    const itemsLeftTextElement: HTMLElement =
      screen.getByTestId("items-left-text");
    expect(itemsLeftTextElement).toHaveTextContent("Bookmarks left");

    expect(screen.queryByTestId("upsell-upgrade-button")).toBeInTheDocument();
  });

  it("should not render BookmarkListsUpsell(Premium)", () => {
    const handleClick = jest.fn();
    renderWithProviders(<BookmarkListsUpsell isPremium={true} />);

    expect(screen.queryByTestId("title1")).not.toBeInTheDocument();
    expect(screen.queryByTestId("title2")).not.toBeInTheDocument();
    expect(screen.queryByTestId("lists-left-text")).not.toBeInTheDocument();
    expect(screen.queryByTestId("items-left-text")).not.toBeInTheDocument();
  });
});
