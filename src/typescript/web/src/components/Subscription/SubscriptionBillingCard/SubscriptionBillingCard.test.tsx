import { render, screen } from "@testing-library/react";
import { PaymentDetailResponse } from "helpers/stripe";
import SubscriptionBillingCard from "../SubscriptionBillingCard/SubscriptionBillingCard";

describe("components/SubscriptionBillingCard", () => {
  it("should render SubscriptionBillingCard", () => {
    const handleClick = jest.fn();

    const initialSubscription = {
      cancel_at: 1234,
      current_period_end: 1682738830,
      default_payment_method: "pm_1N24RGF5zSuk8EYSe65zoc9S",
      id: "stripe_id",
      plan: {
        amount_decimal: 10,
        amount: 10,
        id: "price_1N23okF5zSuk8EYSv5v0xxjk",
        interval: "year",
        product: "product",
      },
      status: "active",
    };

    const paymentDetail: PaymentDetailResponse = {
      type: "card",
      card: {
        brand: "visa",
        exp_month: 5,
        exp_year: 2023,
        last4: "4242",
      },
    };
    render(
      <SubscriptionBillingCard
        userSubscription={initialSubscription}
        paymentMethodDetail={paymentDetail}
      />
    );

    const button: HTMLElement = screen.getByTestId(
      "manage-payment-method-button"
    );
    expect(button).toBeInTheDocument();

    const cardDetail: HTMLElement = screen.getByTestId("billing-card-detail");
    expect(cardDetail).toHaveTextContent("4242 expiring 5/2023");
  });
});
