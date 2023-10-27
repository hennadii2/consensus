import React from "react";
import { renderWithProviders } from "../../__tests__/renderWithProvider";
import Quartile from "./Quartile";

describe("<Quartile />", () => {
  it("throws an error for invalid quartile values", () => {
    // For values less than 1
    expect(() => renderWithProviders(<Quartile quartile={0} />)).toThrow(
      "Invalid quartile value. Expected a number between 1 and 4."
    );

    // For values greater than 4
    expect(() => renderWithProviders(<Quartile quartile={5} />)).toThrow(
      "Invalid quartile value. Expected a number between 1 and 4."
    );

    // For decimal values
    expect(() => renderWithProviders(<Quartile quartile={2.5} />)).toThrow(
      "Invalid quartile value. Expected a number between 1 and 4."
    );
  });

  it("renders 'UNKNOWN' when quartile is null", () => {
    const { getByText, queryByRole } = renderWithProviders(
      <Quartile quartile={null} />
    );

    // Check that the "UNKNOWN" text is displayed
    expect(getByText("UNKNOWN")).toBeInTheDocument();

    // Check that no bubbles are rendered
    const bubbles = queryByRole("img");
    expect(bubbles).toBeNull();
  });
  it("renders the correct number of bubbles", () => {
    const { getAllByRole } = renderWithProviders(<Quartile quartile={1} />);
    const bubbles = getAllByRole("img");
    expect(bubbles.length).toBe(4);
  });

  it("fills all bubbles with bg-green-500 color for quartile 1", () => {
    const { container } = renderWithProviders(<Quartile quartile={1} />);
    const filledBubbles = container.querySelectorAll(".bg-green-500");
    expect(filledBubbles.length).toBe(4);
  });

  it("fills all bubbles with bg-yellow-450 color for quartile 2 and 3", () => {
    for (let i = 2; i <= 2; i++) {
      const { container } = renderWithProviders(<Quartile quartile={i} />);
      const filledBubbles = container.querySelectorAll(".bg-yellow-450");
      expect(filledBubbles.length).toBe(5 - i);
    }
  });

  it("fills all bubbles with bg-red-550 color for quartile 4", () => {
    const { container } = renderWithProviders(<Quartile quartile={4} />);
    const filledBubbles = container.querySelectorAll(".bg-red-550");
    expect(filledBubbles.length).toBe(1);
  });

  it("has the rest of the bubbles with bg-gray-250", () => {
    const { container } = renderWithProviders(<Quartile quartile={3} />);
    const unfilledBubbles = container.querySelectorAll(".bg-gray-250");
    expect(unfilledBubbles.length).toBe(2);
  });
});
