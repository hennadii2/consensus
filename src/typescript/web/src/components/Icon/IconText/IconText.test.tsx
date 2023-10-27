import { render, screen } from "@testing-library/react";
import { IconText } from "components/Icon";

describe("components/IconText", () => {
  it("should render icon text", () => {
    render(<IconText title="Title" icon="upload" items={["Hello"]} />);

    const iconText = screen.getByTestId("icon-text");

    expect(iconText).toBeInTheDocument();
  });

  it("should render icon text with item", () => {
    render(<IconText title="Title" icon="upload" items={["Hello"]} />);

    const iconText = screen.getByText("Hello");

    expect(iconText).toBeInTheDocument();
  });
});
