import { fireEvent, render, screen } from "@testing-library/react";
import Switch from "components/Switch";
import { Provider } from "react-redux";
import { store } from "store/index";

describe("components/Switch", () => {
  it("should render switch", () => {
    let value = false;

    render(
      <Provider store={store}>
        <Switch
          onChange={() => {
            value = true;
          }}
        />
      </Provider>
    );

    const content: HTMLButtonElement = screen.getByTestId("switch");
    fireEvent.click(content);

    expect(content).toBeInTheDocument();
    expect(value).toBe(true);
  });
});
