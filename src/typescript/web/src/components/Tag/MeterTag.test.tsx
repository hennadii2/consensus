import { render, screen } from "@testing-library/react";
import MeterTag from "./MeterTag";

describe("components/MeterTag", () => {
  it("should render MeterTag", () => {
    render(<MeterTag />);

    const content: HTMLButtonElement = screen.getByTestId("meter-tag");
    expect(content).toBeInTheDocument();
    expect(content).toHaveTextContent("");
  });

  it("should render Yes", () => {
    render(<MeterTag meter="YES" />);

    const content: HTMLButtonElement = screen.getByTestId("meter-tag");
    expect(content).toHaveTextContent("Yes");
  });

  it("should render No", () => {
    render(<MeterTag meter="NO" />);

    const content: HTMLButtonElement = screen.getByTestId("meter-tag");
    expect(content).toHaveTextContent("No");
  });
});
