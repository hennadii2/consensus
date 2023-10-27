import { render, screen } from "@testing-library/react";
import mockRouter from "next-router-mock";
import Page from "../pages/index";
import TRENDING from "./data/trending.json";
import TestProvider from "./TestProvider";

jest.mock("next/head", () => {
  return {
    __esModule: true,
    default: ({ children }: { children: Array<React.ReactElement> }) => {
      return <>{children}</>;
    },
  };
});

jest.mock("next/router", () => require("next-router-mock"));

describe("pages/index", () => {
  it("should render", () => {
    mockRouter.push("/search");
    render(
      <TestProvider>
        <Page
          questionTypes={TRENDING.question_types}
          topics={TRENDING.topics}
          trendings={[]}
        />
      </TestProvider>
    );

    const paragraph: HTMLParagraphElement = screen.getByTestId("subtitle");

    expect(paragraph).toBeInTheDocument();
  });

  it("should render trending queries", () => {
    render(
      <TestProvider>
        <Page
          questionTypes={TRENDING.question_types}
          topics={TRENDING.topics}
          trendings={["social media and mental health"]}
        />
      </TestProvider>
    );

    const trending: HTMLElement = screen.getByText(
      "social media and mental health"
    );

    expect(trending).toBeInTheDocument();
  });

  it("should render open graph", () => {
    const { container } = render(
      <TestProvider>
        <Page
          questionTypes={TRENDING.question_types}
          topics={TRENDING.topics}
          trendings={["social media and mental health"]}
        />
      </TestProvider>
    );

    expect(
      container.querySelector('[property="og:title"]')
    ).toBeInTheDocument();
    expect(
      container.querySelector('[property="twitter:title"]')
    ).toBeInTheDocument();

    expect(
      container.querySelector('[property="description"]')
    ).toBeInTheDocument();
    expect(
      container.querySelector('[property="og:description"]')
    ).toBeInTheDocument();
    expect(
      container.querySelector('[property="twitter:description"]')
    ).toBeInTheDocument();

    expect(container.querySelector('[property="og:type"]')).toBeInTheDocument();
    expect(container.querySelector('[property="og:url"]')).toBeInTheDocument();

    expect(
      container.querySelector('[property="og:image"]')
    ).toBeInTheDocument();
    expect(
      container.querySelector('[property="twitter:image"]')
    ).toBeInTheDocument();

    expect(
      container.querySelector('[property="og:image:alt"]')
    ).toBeInTheDocument();
    expect(
      container.querySelector('[property="twitter:image:alt"]')
    ).toBeInTheDocument();

    expect(
      container.querySelector('[property="twitter:card"]')
    ).toBeInTheDocument();
    expect(
      container.querySelector('[property="twitter:site"]')
    ).toBeInTheDocument();
  });

  it("should render question_types", () => {
    render(
      <TestProvider>
        <Page
          questionTypes={TRENDING.question_types}
          topics={TRENDING.topics}
          trendings={[]}
        />
      </TestProvider>
    );

    const titleContent: HTMLParagraphElement[] = screen.getAllByText(
      TRENDING.question_types[0].title
    );

    expect(titleContent[0]).toBeInTheDocument();

    const content: HTMLParagraphElement[] = screen.getAllByText(
      TRENDING.question_types[0].queries[0]
    );

    expect(content[0]).toBeInTheDocument();
  });

  it("should render topics", () => {
    render(
      <TestProvider>
        <Page
          questionTypes={TRENDING.question_types}
          topics={TRENDING.topics}
          trendings={[]}
        />
      </TestProvider>
    );

    const titleContent: HTMLParagraphElement[] = screen.getAllByText(
      TRENDING.topics[0].title
    );

    expect(titleContent[0]).toBeInTheDocument();

    const content: HTMLParagraphElement[] = screen.getAllByText(
      TRENDING.topics[0].queries[0]
    );

    expect(content[0]).toBeInTheDocument();
  });
});
