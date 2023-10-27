import { render, screen } from "@testing-library/react";
import TestProvider from "../../../__tests__/TestProvider";
import NoEduEmailModal from "./NoEduEmailModal";

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

describe("components/NoEduEmailModal", () => {
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

  it("should render no edu email modal", () => {
    render(
      <TestProvider>
        <NoEduEmailModal open onClose={() => {}} />
      </TestProvider>
    );

    const content: HTMLDivElement = screen.getByTestId("no-edu-email-modal");
    expect(content).toBeInTheDocument();

    const text: HTMLAnchorElement = screen.getByText(
      "We could not find a .edu email address associated with your account"
    );
    expect(text.tagName).toBe("H3");
  });
});
