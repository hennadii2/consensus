import { fireEvent, screen } from "@testing-library/react";
import { renderWithProviders } from "../../../__tests__/renderWithProvider";
import SubscriptionCurrentPlanCard from "../SubscriptionCurrentPlanCard/SubscriptionCurrentPlanCard";

describe("components/SubscriptionCurrentPlanCard", () => {
  it("should render SubscriptionCurrentPlanCard(Free)", () => {
    const handleClick = jest.fn();
    renderWithProviders(
      <SubscriptionCurrentPlanCard
        plan_name="Free"
        unit_amount={0}
        interval="month"
        onCancelClick={handleClick}
      />
    );

    const titleElement: HTMLElement = screen.getByTestId("title");
    expect(titleElement).toHaveTextContent("Free Plan");

    const planAmount: HTMLElement = screen.getByTestId(
      "current-plan-card-amount"
    );
    expect(planAmount).toHaveTextContent("$0.00");

    const button: HTMLButtonElement = screen.getByTestId(
      "current-plan-card-cancel-button"
    );
    fireEvent.click(button);
    expect(handleClick).toHaveBeenCalled();

    const featureListElement: HTMLButtonElement =
      screen.getByTestId("feature-list");
    expect(featureListElement).toHaveTextContent(
      "Unlimited searchesUnlimited research quality indicatorsUnlimited AI-powered filters20 AI credits per month for our most powerful AI features: GPT-4 Summaries, Consensus Meters, and Study Snapshots"
    );
  });

  it("should render SubscriptionCurrentPlanCard(Premium)", () => {
    const handleClick = jest.fn();
    const subscription = {
      user: {
        cancel_at: 1234,
        current_period_end: 1682738830,
        default_payment_method: "pm_1N24RGF5zSuk8EYSe65zoc9S",
        id: "subscription_id",
        plan: {
          amount_decimal: 10,
          amount: 10,
          id: "price_1N23okF5zSuk8EYSv5v0xxjk",
          interval: "year",
          product: "product",
        },
        status: "active",
      },
    };
    renderWithProviders(
      <SubscriptionCurrentPlanCard
        plan_name="Premium"
        unit_amount={299}
        interval="month"
        onCancelClick={handleClick}
        subscription={subscription}
      />
    );

    const titleElement: HTMLElement = screen.getByTestId("title");
    expect(titleElement).toHaveTextContent("Premium Plan");

    const planAmount: HTMLElement = screen.getByTestId(
      "current-plan-card-amount"
    );
    expect(planAmount).toHaveTextContent("$2.99");

    const button: HTMLButtonElement = screen.getByTestId(
      "current-plan-card-cancel-button"
    );
    fireEvent.click(button);
    expect(handleClick).toHaveBeenCalled();
  });
});
