import { render, screen } from "@testing-library/react";
import FilterDrawer from "components/FilterDrawer";
import { Provider } from "react-redux";
import { store } from "store/index";

describe("components/FilterDrawer", () => {
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

  it("should render filter drawer", () => {
    render(
      <Provider store={store}>
        <FilterDrawer
          open
          onClose={() => {}}
          value={{
            fieldsOfStudy: "",
            filterControlledStudies: "",
            filterHumanStudies: "",
            sampleSizeMin: "",
            sjrBestQuartileMin: "",
            sjrBestQuartileMax: "",
            studyTypes: "",
            yearMin: "",
          }}
          onChangeFilter={() => {}}
        />
      </Provider>
    );

    const content: HTMLDivElement = screen.getByTestId("filter-drawer");
    expect(content).toBeInTheDocument();

    const title: HTMLAnchorElement = screen.getByText("Filters");
    expect(title.tagName).toBe("H2");
  });
});
