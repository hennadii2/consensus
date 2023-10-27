import { render, screen } from "@testing-library/react";
import Logo from ".";

describe("components/Logo", () => {
  it("should render small logo", () => {
    render(<Logo size="small" />);

    const logo: HTMLImageElement = screen.getByTestId("logo-img");

    expect(logo).toHaveAttribute("src", "/images/logo-min.svg");
  });

  it("should render large logo", () => {
    render(<Logo size="large" />);

    const logo: HTMLImageElement = screen.getByTestId("logo-img");

    expect(logo).toHaveAttribute("src", "/images/logo-full.svg");
  });

  it("should have a background", () => {
    render(<Logo size="small" hasBackground />);

    const logoContainer: HTMLDivElement = screen.getByTestId("logo-bg");

    expect(logoContainer).toHaveClass("bg-white rounded-lg");
  });
});
