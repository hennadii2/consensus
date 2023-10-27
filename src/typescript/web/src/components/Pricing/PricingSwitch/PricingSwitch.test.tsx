import { fireEvent, render, screen } from "@testing-library/react";
import PricingSwitch, {
  PricingSwitchFlag,
} from "components/Pricing/PricingSwitch";
import { Provider } from "react-redux";
import { store } from "store/index";

describe("components/Pricing/PricingSwitch", () => {
  it("should render pricingswitch for monthly", async () => {
    let value = false;

    render(
      <Provider store={store}>
        <PricingSwitch
          onChange={(price?: any) => {
            value = true;
          }}
          initialFlag={PricingSwitchFlag.MONTHLY}
        />
      </Provider>
    );

    const content: HTMLButtonElement = screen.getByTestId(
      "pricing-switch-monthly"
    );
    await fireEvent.click(content);

    expect(content).toBeInTheDocument();
    expect(value).toBe(true);
  });

  it("should render pricingswitch for annually", async () => {
    let value = false;

    render(
      <Provider store={store}>
        <PricingSwitch
          onChange={(price?: any) => {
            value = true;
          }}
          initialFlag={PricingSwitchFlag.ANNUALLY}
        />
      </Provider>
    );

    const content: HTMLButtonElement = screen.getByTestId(
      "pricing-switch-annually"
    );
    await fireEvent.click(content);

    expect(content).toBeInTheDocument();
    expect(value).toBe(true);
  });
});
