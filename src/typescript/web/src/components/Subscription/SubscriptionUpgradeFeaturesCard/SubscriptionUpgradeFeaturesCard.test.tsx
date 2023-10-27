import { screen } from "@testing-library/react";
import { SubscriptionPlan } from "enums/subscription-plans";
import { renderWithProviders } from "../../../__tests__/renderWithProvider";
import SubscriptionUpgradeFeaturesCard from "../SubscriptionUpgradeFeaturesCard/SubscriptionUpgradeFeaturesCard";

describe("components/SubscriptionUpgradeFeaturesCard", () => {
  it("should render SubscriptionUpgradeFeaturesCard(Free)", () => {
    const handleClick = jest.fn();
    renderWithProviders(
      <SubscriptionUpgradeFeaturesCard plan_name={SubscriptionPlan.FREE} />
    );

    const titleElement: HTMLElement = screen.getByTestId("title");
    expect(titleElement).toHaveTextContent("Upgrade for these benefits");

    const featureListElement: HTMLElement = screen.getByTestId("feature-list");
    expect(featureListElement).toHaveTextContent(
      "Unlimited searchesUnlimited research quality indicatorsUnlimited AI-powered filters20 AI credits per month for our most powerful AI features: GPT-4 Summaries, Consensus Meters, and Study Snapshots"
    );
  });

  it("should render SubscriptionUpgradeFeaturesCard(Premium)", () => {
    const handleClick = jest.fn();
    renderWithProviders(
      <SubscriptionUpgradeFeaturesCard plan_name={SubscriptionPlan.PREMIUM} />
    );

    const titleElement: HTMLElement = screen.getByTestId("title");
    expect(titleElement).toHaveTextContent("Upgrade for these benefits");
  });

  it("should render SubscriptionUpgradeFeaturesCard(Enterprise)", () => {
    const handleClick = jest.fn();
    renderWithProviders(
      <SubscriptionUpgradeFeaturesCard
        plan_name={SubscriptionPlan.ENTERPRISE}
      />
    );

    const titleElement: HTMLElement = screen.getByTestId("title");
    expect(titleElement).toHaveTextContent("Upgrade for these benefits");

    const featureListElement: HTMLElement = screen.getByTestId("feature-list");
    expect(featureListElement).toHaveTextContent(
      "Manage accounts for your organisation"
    );
  });
});
