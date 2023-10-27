import { render, screen } from "@testing-library/react";
import ShareModal from "components/ShareModal";
import { Provider } from "react-redux";
import { store } from "store/index";

describe("components/ShareModal", () => {
  beforeEach(() => {
    // IntersectionObserver isn't available in test environment
    const mockIntersectionObserver = jest.fn();
    mockIntersectionObserver.mockReturnValue({
      observe: () => null,
      unobserve: () => null,
      disconnect: () => null,
    });
    window.IntersectionObserver = mockIntersectionObserver;
  });

  it("should render share modal", () => {
    render(
      <Provider store={store}>
        <ShareModal
          open
          title="Share this finding"
          shareText="Share"
          text="Hello"
          onClose={() => {}}
        />
      </Provider>
    );

    const content: HTMLDivElement = screen.getByTestId("share-modal");
    expect(content).toBeInTheDocument();

    const text: HTMLAnchorElement = screen.getByText("Hello");
    expect(text.tagName).toBe("P");

    const title: HTMLAnchorElement = screen.getByText("Share this finding");
    expect(title.tagName).toBe("H3");
  });
});
