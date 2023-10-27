import { render, screen } from "@testing-library/react";
import VerticalDivider from "components/VerticalDivider";

describe("components/VerticalDivider", () => {
  it("should render a vertical divider", () => {
    render(<VerticalDivider />);

    const verticalDivider: HTMLDivElement =
      screen.getByTestId("vertical-divider");

    expect(verticalDivider).toBeInTheDocument();
  });

  it("should render a vertical divider with custom sizing", () => {
    render(<VerticalDivider height={22} width={2} />);

    const verticalDivider: HTMLDivElement =
      screen.getByTestId("vertical-divider");

    expect(verticalDivider).toHaveStyle({
      height: "22px",
      width: "2px",
    });
  });
});
