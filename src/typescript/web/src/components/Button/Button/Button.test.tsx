import { fireEvent, render, screen } from "@testing-library/react";
import Button from "components/Button";

describe("components/Button", () => {
  it("should render button", () => {
    const handleClick = jest.fn();
    render(
      <Button type="button" onClick={handleClick}>
        Load more
      </Button>
    );

    const button: HTMLButtonElement = screen.getByText("Load more");

    expect(button).toBeInTheDocument();
  });

  it("should trigger onClick", () => {
    const handleClick = jest.fn();
    render(
      <Button type="button" onClick={handleClick}>
        Load more
      </Button>
    );

    const button: HTMLButtonElement = screen.getByText("Load more");
    fireEvent.click(button);

    expect(handleClick).toHaveBeenCalled();
  });

  it("should have className", () => {
    const handleClick = jest.fn();
    render(
      <Button type="button" className="button-classname" onClick={handleClick}>
        Load more
      </Button>
    );

    const button: HTMLButtonElement = screen.getByText("Load more");

    expect(button).toHaveClass("button-classname");
  });

  it("should have loading", () => {
    render(
      <Button type="button" isLoading={true}>
        Load more
      </Button>
    );

    const loading: HTMLSpanElement = screen.getByText("...");

    expect(loading).toHaveClass("loading-dot");
  });
});
