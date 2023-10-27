import { fireEvent, render, screen } from "@testing-library/react";
import { ClaimButton } from "components/Button";

describe("components/ClaimButton", () => {
  it("should render ClaimButton", () => {
    const handleClick = jest.fn();
    render(<ClaimButton onClick={handleClick}>Claim Button</ClaimButton>);

    const button: HTMLButtonElement = screen.getByText("Claim Button");

    expect(button).toBeInTheDocument();
  });

  it("should trigger onClick", () => {
    const handleClick = jest.fn();
    render(<ClaimButton onClick={handleClick}>Claim Button</ClaimButton>);

    const button: HTMLButtonElement = screen.getByText("Claim Button");
    fireEvent.click(button);

    expect(handleClick).toHaveBeenCalled();
  });

  it("should have an upload-icon", () => {
    const handleClick = jest.fn();
    render(<ClaimButton onClick={handleClick}>Claim Button</ClaimButton>);

    const icon = screen.getByTestId("upload-icon");

    expect(icon).toBeInTheDocument();
  });
});
