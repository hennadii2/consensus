import { render, screen } from "@testing-library/react";
import Head from "./Head";

jest.mock("next/head", () => {
  return {
    __esModule: true,
    default: ({ children }: { children: Array<React.ReactElement> }) => {
      return <>{children}</>;
    },
  };
});

const TITLE = "Hello";
const DESCRIPTION = "description";
const TYPE = "website";
const URL = "https://consensus.com";
const IMAGE = "https://consensus.com/images/meta-image.png";
const IMAGE_ALT = "An image of the Consensus logo";
const SCHEMA = JSON.stringify({ "@context": "http://schema.org" });

describe("components/Head", () => {
  it("should render title", () => {
    const { container } = render(<Head title={TITLE} />);

    const title: HTMLTitleElement = screen.getByTestId("title");

    expect(title).toHaveTextContent("Hello");

    expect(container.querySelector('[property="og:title"]')).toHaveAttribute(
      "content",
      TITLE
    );
    expect(
      container.querySelector('[property="twitter:title"]')
    ).toHaveAttribute("content", TITLE);
  });

  it("should render description", () => {
    const { container } = render(
      <Head title={TITLE} description={DESCRIPTION} />
    );

    expect(
      container.querySelector('[property="og:description"]')
    ).toHaveAttribute("content", DESCRIPTION);
    expect(
      container.querySelector('[property="twitter:description"]')
    ).toHaveAttribute("content", DESCRIPTION);
  });

  it("should render type", () => {
    const { container } = render(<Head title={TITLE} type={TYPE} />);

    expect(container.querySelector('[property="og:type"]')).toHaveAttribute(
      "content",
      TYPE
    );
  });

  it("should render url", () => {
    const { container } = render(<Head title={TITLE} url={URL} />);

    expect(container.querySelector('[property="og:url"]')).toHaveAttribute(
      "content",
      URL
    );
  });

  it("should render image", () => {
    const { container } = render(<Head title={TITLE} image={IMAGE} />);

    expect(container.querySelector('[property="og:image"]')).toHaveAttribute(
      "content",
      IMAGE
    );
    expect(
      container.querySelector('[property="twitter:image"]')
    ).toHaveAttribute("content", IMAGE);
  });

  it("should render image alt", () => {
    const { container } = render(<Head title={TITLE} imageAlt={IMAGE_ALT} />);

    expect(
      container.querySelector('[property="og:image:alt"]')
    ).toHaveAttribute("content", IMAGE_ALT);
    expect(
      container.querySelector('[property="twitter:image:alt"]')
    ).toHaveAttribute("content", IMAGE_ALT);
  });

  it("should render schema", () => {
    const { container } = render(<Head title={TITLE} schema={SCHEMA} />);

    expect(
      container.querySelector('[type="application/ld+json"]')
    ).toHaveTextContent(SCHEMA);
  });
});
