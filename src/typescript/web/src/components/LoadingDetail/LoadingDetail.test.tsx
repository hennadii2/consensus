import { render, screen } from "@testing-library/react";
import LoadingDetail from "components/LoadingDetail";
import { Provider } from "react-redux";
import { store } from "store/index";

describe("components/LoadingDetail", () => {
  it("should render loadingdetail", () => {
    render(
      <Provider store={store}>
        <LoadingDetail />
      </Provider>
    );

    const loadingdetail: HTMLDivElement = screen.getByTestId("loadingdetail");

    expect(loadingdetail).toBeInTheDocument();
  });
});
