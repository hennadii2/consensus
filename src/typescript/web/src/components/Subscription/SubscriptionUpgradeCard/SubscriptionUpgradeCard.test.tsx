import { fireEvent, screen } from "@testing-library/react";
import { SubscriptionPlan } from "enums/subscription-plans";
import SubscriptionUpgradeCard from "../SubscriptionUpgradeCard/SubscriptionUpgradeCard";
import { renderWithProviders } from "./../../../__tests__/renderWithProvider";

describe("components/SubscriptionUpgradeCard", () => {
  it("should render SubscriptionUpgradeCard(PREMIUM)", () => {
    const handleClick = jest.fn();
    renderWithProviders(
      <SubscriptionUpgradeCard
        upgradePlan={SubscriptionPlan.PREMIUM}
        unit_amount={1599}
        interval={"Year"}
        onClick={handleClick}
      />
    );

    const titleElement: HTMLElement = screen.getByTestId("title");
    expect(titleElement).toHaveTextContent(
      "Want unlimited? Upgrade to Premium."
    );

    const amountElement: HTMLElement = screen.getByTestId(
      "upgrade-plan-card-amount"
    );
    expect(amountElement).toHaveTextContent("$15.99");

    const upgradeButton: HTMLElement = screen.getByTestId(
      "upgrade-card-button"
    );
    expect(upgradeButton).toHaveTextContent("Upgrade plan");

    fireEvent.click(upgradeButton);
    expect(handleClick).toHaveBeenCalled();
  });

  it("should render SubscriptionUpgradeCard(Enterprise)", () => {
    const handleClick = jest.fn();
    renderWithProviders(
      <SubscriptionUpgradeCard
        upgradePlan={SubscriptionPlan.ENTERPRISE}
        unit_amount={1500}
        interval={"Year"}
      />
    );

    const titleElement: HTMLElement = screen.getByTestId("title");
    expect(titleElement).toHaveTextContent(
      "Need teamwork? Upgrade to Enterprise:"
    );

    const upgradeButton: HTMLElement = screen.getByTestId(
      "upgrade-card-button"
    );
    expect(upgradeButton).toHaveTextContent("Contact sales");
  });
});
