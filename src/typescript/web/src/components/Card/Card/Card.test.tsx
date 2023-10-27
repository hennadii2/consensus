import { render, screen } from "@testing-library/react";
import Card from "components/Card";

describe("components/Card", () => {
  it("should render card", () => {
    render(<Card>this is a card</Card>);

    const card: HTMLDivElement = screen.getByTestId("card");

    expect(card).toBeInTheDocument();
  });

  it("should render the children", () => {
    render(<Card>this is a card</Card>);

    const card: HTMLDivElement = screen.getByText("this is a card");

    expect(card).toBeInTheDocument();
  });

  it("should have default styling using classNames", () => {
    render(<Card>this is a card</Card>);

    const card: HTMLDivElement = screen.getByTestId("card");

    expect(card).toHaveClass(
      "bg-white bg-opacity-70 rounded-3xl p-[26px] shadow-card"
    );
  });

  it("should have add className", () => {
    render(<Card className="card-classname">this is a card</Card>);

    const card: HTMLDivElement = screen.getByTestId("card");

    expect(card).toHaveClass("card-classname");
  });
});
