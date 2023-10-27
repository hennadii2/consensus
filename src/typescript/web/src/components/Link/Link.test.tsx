import { render, screen } from "@testing-library/react";
import Link from "components/Link";

describe("components/Link", () => {
  it("should render link", () => {
    render(<Link>This is a link</Link>);

    const link = screen.getByTestId("blue-colored-link");

    expect(link).toBeInTheDocument();
  });

  it("should have text", () => {
    render(<Link>This is a link</Link>);

    const link = screen.getByText("This is a link");

    expect(link).toBeInTheDocument();
  });

  it("should have a className of text-blue-600", () => {
    render(<Link>This is a link</Link>);

    const link = screen.getByTestId("blue-colored-link");

    expect(link).toHaveClass("text-blue-600");
  });
});
