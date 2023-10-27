import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axios from "axios";
import { IDetailItem } from "components/DetailContent/DetailContent";
import path from "constants/path";
import { StudyType } from "helpers/api";
import { GetServerSidePropsContext } from "next";
import { ParsedUrlQuery } from "querystring";
import api from "../helpers/apiInstance";
import Page, { getServerSidePropsDetail } from "../pages/details/[title]/[id]";
import TestProvider from "./TestProvider";

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
      query: {},
      asPath: "",
    };
  },
}));

export const item: IDetailItem = {
  claim: {
    id: "1",
    text: "Both Pfizer and Moderna",
    url_slug: "hello",
  },
  paper: {
    id: "12",
    title:
      "Evaluation of dietary creatine and guanidinoacetic acid supplementation in juvenile red drumSciaenops ocellatus",
    abstract:
      "The SARS-CoV-2 Delta (B.1.617.2) variant of concern is expanding globally. Here, we assess real-world effectiveness of the BNT162b2 (Pfizer-BioNTech) and mRNA-1273 (Moderna) vaccines against this variant by conducting a Meta-Analysis of several studies. BNT162b2 effectiveness against any Delta infection, symptomatic or asymptomatic, was 64.2% (95% CI: 38.1-80.1%) [≥]14 days after the first dose and before the second dose, but was only 53.5% (95% CI: 43.9-61.4%) [≥]14 days after the second dose, in a population in which a large proportion of fully vaccinated persons received their second dose several months earlier. Corresponding effectiveness measures for mRNA-1273 were 79.0% (95% CI: 58.9-90.1%) and 84.8% (95% CI: 75.9-90.8%), respectively. Effectiveness against any severe, critical, or fatal COVID-19 disease due to Delta was 89.7% (95% CI: 61.0-98.1%) for BNT162b2 and 100.0% (95% CI: 41.2-100.0%) for mRNA-1273, [≥]14 days after the second dose. Both BNT162b2 and mRNA-1273 are highly effective in preventing Delta hospitalization and death, but less so in preventing infection, particularly for BNT162b2.",
    authors: ["author", "author 1", "author 2", "author 3"],
    abstract_takeaway: "abstract takeaway",
    badges: {
      very_rigorous_journal: true,
      rigorous_journal: false,
      highly_cited_paper: true,
      study_type: StudyType.RCT,
      disputed: {
        url: "https://go.com",
        reason: "",
      },
      sample_size: 1,
      study_count: 1,
      animal_trial: true,
      large_human_trial: true,
      enhanced: true,
    },
    volume: "12",
    pages: "1-4",
    citation_count: 10,
    provider_url: "https://consensus.app",
    doi: "10.1016/S1052-5149(02)00023-0",
    journal: {
      title: "Journal Title",
      scimago_quartile: 1,
    },
    year: 2012,
    url_slug: "paper-title-author",
    publish_date: "12 June",
  },
};

describe("pages/details", () => {
  it("should render", async () => {
    render(
      <TestProvider>
        <Page id="1234" item={item} />
      </TestProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("result-claim")).toBeInTheDocument();
    });
    const paragraph: HTMLParagraphElement = screen.getByText("Key Takeaway");

    expect(paragraph).toBeInTheDocument();
  });

  it("should have content", async () => {
    render(
      <TestProvider>
        <Page id="1234" item={item} />
      </TestProvider>
    );
    await waitFor(() => {
      expect(screen.getByTestId("result-claim")).toBeInTheDocument();
    });
    const paperTitle: HTMLParagraphElement = screen.getByTestId("paper-title");

    expect(paperTitle).toHaveTextContent(item.paper.title);

    const journalTitle: HTMLParagraphElement =
      screen.getByTestId("journal-title");

    expect(journalTitle).toHaveTextContent(item.paper.journal.title);

    const abstract: HTMLParagraphElement = screen.getByTestId("abstract");

    expect(abstract).toHaveTextContent(item.paper.abstract);
  });

  it("should have title", async () => {
    render(
      <TestProvider>
        <Page id="1234" item={item} />
      </TestProvider>
    );
    await waitFor(() => {
      expect(screen.getByTestId("result-claim")).toBeInTheDocument();
    });

    const title: HTMLTitleElement = screen.getByTestId("title");
    expect(title).toHaveTextContent(`${item.paper.title} - Consensus`);
  });

  it("should have doi url", async () => {
    render(
      <TestProvider>
        <Page id="1234" item={item} />
      </TestProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("result-claim")).toBeInTheDocument();
    });

    const link: HTMLAnchorElement = screen.getByTestId("full-text-link");
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", `https://doi.org/${item.paper.doi}`);
  });

  it("should have provider url", async () => {
    render(
      <TestProvider>
        <Page id="1234" item={item} />
      </TestProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("result-claim")).toBeInTheDocument();
    });

    const link: HTMLAnchorElement = screen.getByTestId("semantic-scholar-link");
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", item.paper.provider_url);
  });

  it("should have message when journal name is empty", async () => {
    render(
      <TestProvider>
        <Page
          id="333"
          item={
            {
              ...item,
              paper: {
                ...item.paper,
                journal: {
                  title: "",
                },
              },
            } as IDetailItem
          }
        />
      </TestProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("result-claim")).toBeInTheDocument();
    });

    const journal: HTMLAnchorElement = screen.getByTestId("journal-title");
    expect(journal).toBeInTheDocument();
    expect(journal).toHaveTextContent(
      "Journal name not available for this finding"
    );
  });

  it("should render open graph", async () => {
    const { container } = render(
      <TestProvider>
        <Page id="1234" item={item} />
      </TestProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("result-claim")).toBeInTheDocument();
    });

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
      `${item.paper.title} - Consensus`
    );
  });

  it("should render findingmissing", async () => {
    render(
      <TestProvider>
        <Page id="missing" item={null} />
      </TestProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("findingmissing")).toBeInTheDocument();
    });

    await new Promise((resolve) => setTimeout(resolve, 4000));

    await waitFor(() => {
      expect(screen.getByTestId("findingmissing")).toBeInTheDocument();
    });
  });

  it("should redirect to internal server error", async () => {
    const mockAxios = api as jest.Mocked<typeof axios>;

    mockAxios.get.mockRejectedValue({
      isAxiosError: true,
      response: {
        data: { message: "Failed to get claim details" },
        status: 500,
      },
    });

    const context = {
      req: {
        headers: {},
      },
      query: {
        id: item.claim?.id,
        title: item.claim?.url_slug,
      } as ParsedUrlQuery,
    };
    const value = (await getServerSidePropsDetail(
      context as GetServerSidePropsContext
    )) as any;

    expect(value.redirect).toEqual({
      destination: path.INTERNAL_SERVER_ERROR,
      permanent: false,
    });
  });

  it("should redirect to too many requests", async () => {
    const mockAxios = api as jest.Mocked<typeof axios>;

    mockAxios.get.mockRejectedValue({
      isAxiosError: true,
      response: {
        data: { message: "Failed to get claim details" },
        status: 429,
      },
    });

    const context = {
      req: {
        headers: {},
      },
      query: {
        id: item.claim?.id,
        title: item.claim?.url_slug,
      } as ParsedUrlQuery,
    };
    const value = (await getServerSidePropsDetail(
      context as GetServerSidePropsContext
    )) as any;

    expect(value.redirect).toEqual({
      destination: path.TOO_MANY_REQUESTS,
      permanent: false,
    });
  });

  it("should show more author", async () => {
    render(
      <TestProvider>
        <Page id="1234" item={item} />
      </TestProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("result-claim")).toBeInTheDocument();
    });

    expect(screen.queryByTestId("show-more-author")).not.toBeInTheDocument();
    expect(screen.queryByTestId("hide-more-author")).toBeInTheDocument();
    expect(screen.queryByTestId("hide-more-author")).toHaveTextContent(
      "author, author 1, author 2 + 1 more authors"
    );

    const moreButton = screen.getByTestId("more-author-button");
    expect(moreButton).toBeInTheDocument();
    await userEvent.click(moreButton);

    expect(screen.queryByTestId("hide-more-author")).not.toBeInTheDocument();
    expect(screen.queryByTestId("show-more-author")).toBeInTheDocument();
    expect(screen.queryByTestId("show-more-author")).toHaveTextContent(
      "author, author 1, author 2, author 3"
    );
  });
});
