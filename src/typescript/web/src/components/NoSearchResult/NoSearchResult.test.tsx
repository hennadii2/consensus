import { render, screen } from "@testing-library/react";
import NoSearchResult from "components/NoSearchResult";
import { Provider } from "react-redux";
import { store } from "store/index";

describe("components/NoSearchResult", () => {
  it("should render nosearchresult", () => {
    render(
      <Provider store={store}>
        <NoSearchResult />
      </Provider>
    );

    const nosearchresult: HTMLDivElement = screen.getByTestId("nosearchresult");

    expect(nosearchresult).toBeInTheDocument();
  });
});
