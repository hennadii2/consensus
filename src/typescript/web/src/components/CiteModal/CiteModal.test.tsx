import { render, screen } from "@testing-library/react";
import CiteModal from "components/CiteModal";
import { Provider } from "react-redux";
import { store } from "store/index";

describe("components/CiteModal", () => {
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

  it("should render cite modal", () => {
    render(
      <Provider store={store}>
        <CiteModal
          open
          title="Cite this finding"
          apa=""
          bibtex=""
          chicago=""
          mla=""
          harvard=""
          onClose={() => {}}
        />
      </Provider>
    );

    const content: HTMLDivElement = screen.getByTestId("cite-modal");
    expect(content).toBeInTheDocument();

    const title: HTMLAnchorElement = screen.getByText("Cite this finding");
    expect(title.tagName).toBe("H3");
  });
});
