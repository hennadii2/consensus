import { render, screen } from "@testing-library/react";
import axios from "axios";
import SEARCH_ITEMS from "../constants/results.json";
import api from "../helpers/apiInstance";
import Page from "../pages/results";
import TestProvider from "./TestProvider";
import { waitFor } from "./utils/waitFor";

jest.mock("../helpers/apiInstance");

jest.mock("next/head", () => {
  return {
    __esModule: true,
    default: ({ children }: { children: Array<React.ReactElement> }) => {
      return <>{children}</>;
    },
  };
});

jest.mock("next/router", () => ({
  useRouter() {
    return {
      route: "/",
      pathname: "",
      query: {
        q: "test",
      },
      asPath: "",
      push: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
      },
      beforePopState: jest.fn(() => null),
      prefetch: jest.fn(() => null),
    };
  },
}));

describe("pages/results", () => {
  it("should have results", async () => {
    jest.setTimeout(30000);
    const mockAxios = api as jest.Mocked<typeof axios>;

    mockAxios.get.mockResolvedValue({
      data: SEARCH_ITEMS,
    });

    render(
      <TestProvider>
        <Page isTest={true} />
      </TestProvider>
    );

    await waitFor(() => screen.findAllByTestId("card-search-result-item"));

    const content: HTMLParagraphElement[] = screen.getAllByText("Hello World");

    expect(content[0]).toBeInTheDocument();
    expect(content.length).toBe(5);
  });

  it("should render meter", () => {
    render(
      <TestProvider>
        <Page isTest={true} />
      </TestProvider>
    );

    const meter: HTMLParagraphElement = screen.getByTestId("meter");
    expect(meter).toBeInTheDocument();

    //const paragraph: HTMLParagraphElement = screen.getByTestId("query-text-no-meter");
    //expect(paragraph).not.toBeInTheDocument();
  });

  it("should have title", () => {
    render(
      <TestProvider>
        <Page isTest={true} />
      </TestProvider>
    );

    const title: HTMLTitleElement = screen.getByTestId("title");
    expect(title).toHaveTextContent("test - Consensus");
  });

  it("should render open graph", () => {
    const { container } = render(
      <TestProvider>
        <Page isTest={true} />
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

    expect(container.querySelector('[property="og:title"]')).toHaveAttribute(
      "content",
      "test - Consensus"
    );
  });

  it("should render no search result", async () => {
    const mockAxios = api as jest.Mocked<typeof axios>;

    mockAxios.get.mockResolvedValue({
      data: { claims: [] },
    });

    render(
      <TestProvider>
        <Page isTest={true} />
      </TestProvider>
    );

    await waitFor(() => screen.getByTestId("nosearchresult"));
    const div: HTMLDivElement = screen.getByTestId("nosearchresult");

    expect(div).toBeInTheDocument();

    await waitFor(() => screen.getByTestId("filter-button"));
    const yearPicker: HTMLDivElement = screen.getByTestId("filter-button");

    expect(yearPicker).toBeInTheDocument();
  });
});
