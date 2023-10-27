import { render, screen } from "@testing-library/react";
import Icon from "./Icon";

describe("components/Icon", () => {
  it("should render icon", () => {
    render(<Icon name="upload" />);

    const icon = screen.getByTestId("icon");

    expect(icon).toBeInTheDocument();
  });
});
