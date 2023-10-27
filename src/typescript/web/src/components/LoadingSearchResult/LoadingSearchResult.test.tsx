import { render, screen } from "@testing-library/react";
import LoadingSearchResult from "components/LoadingSearchResult";
import { Provider } from "react-redux";
import { store } from "store/index";

describe("components/LoadingSearchResult", () => {
  it("should render loadingsearchresult", () => {
    render(
      <Provider store={store}>
        <LoadingSearchResult />
      </Provider>
    );

    const loadingsearchresult: HTMLDivElement = screen.getByTestId(
      "loadingsearchresult"
    );

    expect(loadingsearchresult).toBeInTheDocument();
  });
});
