import { render, screen } from "@testing-library/react";
import Badge from "components/Badge";

describe("components/Badge", () => {
  it("should render badge", () => {
    render(<Badge>1</Badge>);

    const badge: HTMLDivElement = screen.getByTestId("badge");

    expect(badge).toBeInTheDocument();
  });

  it("should have a content", () => {
    render(<Badge>approved</Badge>);

    const badge: HTMLDivElement = screen.getByText("approved");

    expect(badge).toBeInTheDocument();
  });
});
