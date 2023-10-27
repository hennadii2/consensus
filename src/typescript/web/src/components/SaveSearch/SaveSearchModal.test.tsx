import { render, screen } from "@testing-library/react";
import TestProvider from "../../__tests__/TestProvider";
import SaveSearchModal from "./SaveSearchModal";

jest.mock("next/router", () => ({
  useRouter() {
    return {
      route: "/",
      pathname: "",
      query: {
        q: "test",
      },
      asPath: "",
      push: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
      },
      beforePopState: jest.fn(() => null),
      prefetch: jest.fn(() => null),
    };
  },
}));

describe("components/SaveSearchModal", () => {
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

  it("should render savesearch modal", () => {
    render(
      <TestProvider>
        <SaveSearchModal open onClose={() => {}} />
      </TestProvider>
    );

    const content: HTMLDivElement = screen.getByTestId("save-search-modal");
    expect(content).toBeInTheDocument();

    const text: HTMLAnchorElement = screen.getByText("Save to a list");
    expect(text.tagName).toBe("H3");
  });
});
