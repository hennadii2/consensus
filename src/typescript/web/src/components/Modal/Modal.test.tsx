import { screen } from "@testing-library/react";
import { renderWithProviders } from "../../__tests__/renderWithProvider";
import Modal from "./Modal";

const ITEM = {
  id: "1",
  text: "Text",
  score: 1,
  url_slug: "sort-name",
  journal: "Hello World",
  primary_author: "Magdalena",
  year: 2022,
};

describe("components/Modal", () => {
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

  it("should render Modal", () => {
    renderWithProviders(<Modal open={true} onClose={() => {}} />);

    const div = screen.getByTestId("modal");

    expect(div).toBeInTheDocument();
  });
});
