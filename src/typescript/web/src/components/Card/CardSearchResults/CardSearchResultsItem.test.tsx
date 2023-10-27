import { screen } from "@testing-library/react";
import { StudyType } from "helpers/api";
import mockRouter from "next-router-mock";
import { renderWithProviders } from "../../../__tests__/renderWithProvider";
import CardSearchResultsItem from "./CardSearchResultsItem";

const ITEM = {
  id: "1",
  text: "Text",
  paper_id: "3",
  title: "Title",
  score: 1,
  url_slug: "sort-name",
  journal: "Hello World",
  volume: "1",
  pages: "10-12p",
  primary_author: "Magdalena",
  year: 2022,
  badges: {
    very_rigorous_journal: true,
    rigorous_journal: false,
    highly_cited_paper: true,
    study_type: StudyType.RCT,
    sample_size: undefined,
    study_count: undefined,
    animal_trial: undefined,
    large_human_trial: undefined,
    disputed: undefined,
    enhanced: true,
  },
};

const ITEM_WITHOUT_ENHANCED = {
  ...ITEM,
  badges: {
    ...ITEM.badges,
    enhanced: false,
  },
};

jest.mock("next/router", () => require("next-router-mock"));

describe("components/Card/CardSearchResultsItem", () => {
  mockRouter.push("/results");

  it("should render CardSearchResultsItem", () => {
    renderWithProviders(<CardSearchResultsItem index={0} item={ITEM} />);

    const div: HTMLDivElement = screen.getByTestId("card-search-result-item");

    expect(div).toBeInTheDocument();
  });

  it("should render text", () => {
    renderWithProviders(<CardSearchResultsItem index={0} item={ITEM} />);

    const link: HTMLElement = screen.getByTestId("result-item-link");

    expect(link).toHaveTextContent("Text");
  });

  it("should render link", () => {
    renderWithProviders(<CardSearchResultsItem index={0} item={ITEM} />);

    const link: HTMLAnchorElement = screen.getByTestId("result-item-link");

    expect(link).toHaveAttribute("href", "/details/sort-name/1");
  });

  it("should render journal", () => {
    renderWithProviders(<CardSearchResultsItem index={0} item={ITEM} />);

    const element = screen.getByTestId("detail-extras-journal");

    expect(element).toHaveTextContent("Hello World");
  });

  it("should render author", () => {
    renderWithProviders(<CardSearchResultsItem index={0} item={ITEM} />);

    const element = screen.getByTestId("detail-extras-author");

    expect(element).toHaveTextContent("Magdalena et al.");
  });

  it("should render meter tag", () => {
    renderWithProviders(
      <CardSearchResultsItem index={0} item={ITEM} meter="YES" />
    );

    const element = screen.getByTestId("meter-tag");

    expect(element).toHaveTextContent("Yes");
  });

  it("should render enhanced indicator", () => {
    renderWithProviders(<CardSearchResultsItem index={0} item={ITEM} />);

    const div: HTMLDivElement = screen.getByTestId("enhanced-indicator");

    expect(div).toBeInTheDocument();
  });

  it("should not render enhanced indicator", () => {
    renderWithProviders(
      <CardSearchResultsItem index={0} item={ITEM_WITHOUT_ENHANCED} />
    );

    const div = screen.queryByTestId("enhanced-indicator");

    expect(div).toBeNull();
  });
});
