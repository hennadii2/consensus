import { render, screen } from "@testing-library/react";
import FeatureFlagItem from "./FeatureFlagItem";

describe("components/FeatureFlagItem", () => {
  it("should render FeatureFlagItem", () => {
    render(
      <FeatureFlagItem onChange={() => {}} features={[]} name="tes">
        Test
      </FeatureFlagItem>
    );

    const div: HTMLDivElement = screen.getByTestId("feature-flag-item");

    expect(div).toBeInTheDocument();
  });

  it("should checked", () => {
    render(
      <FeatureFlagItem onChange={() => {}} features={["tes"]} name="tes">
        Test
      </FeatureFlagItem>
    );

    const input: HTMLInputElement = screen.getByTestId("feature-flag-input");
    expect(input.checked).toEqual(true);
  });
});
