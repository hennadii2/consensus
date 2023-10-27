import { screen } from "@testing-library/react";
import { renderWithProviders } from "./../../__tests__/renderWithProvider";
import StudySnapshotUpgradePremium from "./StudySnapshotUpgradePremium";

describe("components/StudySnapshot/StudySnapshotUpgradePremium", () => {
  it("should render StudySnapshotUpgradePremium", () => {
    renderWithProviders(<StudySnapshotUpgradePremium />);

    const premiumText1: HTMLElement = screen.getByTestId(
      "study-snapshot-text1"
    );
    expect(premiumText1).toBeInTheDocument();

    const upgradePremiumButton: HTMLElement = screen.getByTestId(
      "study-snapshot-btn-upgrade-premium"
    );
    expect(upgradePremiumButton).toBeInTheDocument();
  });
});
