import { render, screen } from "@testing-library/react";
import { IconLoader } from "components/Icon";

describe("components/IconLoader", () => {
  it("should render icon loader", () => {
    render(<IconLoader />);

    const iconLoader = screen.getByTestId("icon-loader");

    expect(iconLoader).toBeInTheDocument();
  });
});
