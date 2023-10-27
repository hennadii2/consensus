import { render, screen } from "@testing-library/react";
import TestProvider from "../../../__tests__/TestProvider";
import MergeAccountModal from "./MergeAccountModal";

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

describe("components/MergeAccountModal", () => {
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

  it("should render instruction merge account modal", () => {
    render(
      <TestProvider>
        <MergeAccountModal open onClose={() => {}} />
      </TestProvider>
    );

    const content: HTMLDivElement = screen.getByTestId("merge-account-modal");
    expect(content).toBeInTheDocument();

    const text: HTMLAnchorElement = screen.getByText(
      "Follow this instruction to merge accounts:"
    );
    expect(text.tagName).toBe("H3");
  });
});
