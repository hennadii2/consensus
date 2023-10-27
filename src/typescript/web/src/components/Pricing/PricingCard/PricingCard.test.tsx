import { fireEvent, screen } from "@testing-library/react";
import PricingCard from "components/Pricing/PricingCard";
import { SubscriptionPlan } from "enums/subscription-plans";
import { ISubscriptionData } from "helpers/subscription";
import { renderWithProviders } from "./../../../__tests__/renderWithProvider";

describe("components/Pricing/PricingCard", () => {
  it("should clikable PricingCard", async () => {
    let value = false;
    renderWithProviders(
      <PricingCard
        onClick={(price?: any) => {
          value = true;
        }}
        title={SubscriptionPlan.FREE}
        isTest={true}
      />
    );

    const content: HTMLButtonElement = screen.getByTestId(
      "pricing-card-button"
    );
    await fireEvent.click(content);

    expect(content).toBeInTheDocument();
    expect(value).toBe(true);
  });

  it("should render PricingCard", async () => {
    let product = {
      prices: [
        {
          id: "price_1N23okF5zSuk8EYSv5v0xxjk",
          recurring: {
            interval: "month",
          },
          unit_amount: "500",
        },
      ],
    };

    let price = {
      recurring: {
        interval: "year",
      },
      unit_amount: "1500",
    };

    renderWithProviders(
      <PricingCard
        onClick={(price?: any) => {}}
        title={SubscriptionPlan.FREE}
        product={product}
        price={price}
        isTest={true}
      />
    );

    const content: HTMLElement = screen.getByTestId("pricing-card-unit-amount");
    expect(content).toHaveTextContent("$1.25");

    const content2: HTMLElement = screen.getByTestId("pricing-card-title");
    expect(content2).toHaveTextContent("Free");

    const pricingCardButton: HTMLButtonElement = screen.getByTestId(
      "pricing-card-button"
    );
    expect(pricingCardButton).toHaveTextContent("Try searching for free");
  });

  it("should render PricingCard", async () => {
    let product = {
      prices: [
        {
          id: "price_1N23okF5zSuk8EYSv5v0xxjk",
          recurring: {
            interval: "year",
          },
          unit_amount: "1500",
        },
      ],
      metadata: {
        feature_copy_list: "",
      },
    };

    let subscription: ISubscriptionData = {
      user: {
        cancel_at: 1234,
        current_period_end: 1234,
        id: "stripe_id",
        plan: {
          amount_decimal: 10,
          amount: 10,
          id: "price_1N23okF5zSuk8EYSv5v0xxjk",
          interval: "year",
          product: "product",
        },
        status: "active",
      },
      org: null,
    };

    let price = {
      recurring: {
        interval: "year",
      },
      unit_amount: "1500",
    };

    renderWithProviders(
      <PricingCard
        onClick={(price?: any) => {}}
        title={SubscriptionPlan.PREMIUM}
        product={product}
        subscription={subscription}
        price={price}
        isTest={true}
      />
    );

    const content: HTMLElement = screen.getByTestId("pricing-card-unit-amount");
    expect(content).toHaveTextContent("$1.25");

    const content2: HTMLElement = screen.getByTestId("pricing-card-title");
    expect(content2).toHaveTextContent("Premium");

    const pricingCardButton: HTMLButtonElement = screen.getByTestId(
      "pricing-card-button"
    );
    expect(pricingCardButton).toHaveTextContent("Current plan");
  });
});
