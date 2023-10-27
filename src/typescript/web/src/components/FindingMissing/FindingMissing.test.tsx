import { render, screen } from "@testing-library/react";
import FindingMissing from "components/FindingMissing";
import { Provider } from "react-redux";
import { store } from "store/index";

describe("components/FindingMissing", () => {
  it("should render FindingMissing", () => {
    render(
      <Provider store={store}>
        <FindingMissing />
      </Provider>
    );

    const findingmissing: HTMLDivElement = screen.getByTestId("findingmissing");

    expect(findingmissing).toBeInTheDocument();
  });
});
