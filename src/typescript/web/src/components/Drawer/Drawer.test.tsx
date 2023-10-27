import { screen } from "@testing-library/react";
import { renderWithProviders } from "../../__tests__/renderWithProvider";
import Drawer from "./Drawer";

describe("components/Drawer", () => {
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

  it("should render Drawer", () => {
    renderWithProviders(<Drawer open={true} onClose={() => {}} />);

    const div = screen.getByTestId("drawer");

    expect(div).toBeInTheDocument();
  });
});
