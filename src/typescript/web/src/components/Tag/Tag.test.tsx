import { render, screen } from "@testing-library/react";
import Tag from "components/Tag";

describe("components/Tag", () => {
  it("should render tag", () => {
    render(<Tag q="This is a tag">This is a tag</Tag>);

    const tag: HTMLAnchorElement = screen.getByTestId("tag");

    expect(tag).toBeInTheDocument();
  });

  it("should render an anchor with text", () => {
    render(<Tag q="This is a tag">This is a tag</Tag>);

    const tag: HTMLAnchorElement = screen.getByText("This is a tag");

    expect(tag.tagName).toBe("A");
  });

  it("should render a div with text", () => {
    render(<Tag>This is a tag</Tag>);

    const tag: HTMLDivElement = screen.getByText("This is a tag");

    expect(tag.tagName).toBe("DIV");
  });
});
