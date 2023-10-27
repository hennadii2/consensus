import { fireEvent, render, waitFor } from "@testing-library/react";
import { ISearchItem, StudyType } from "helpers/api";
import TestProvider from "../../../__tests__/TestProvider";
import ExportButton from "./ExportButton";

// Mocking necessary dependencies
jest.mock("helpers/api", () => ({
  ...jest.requireActual("helpers/api"),
  getPapersList: jest.fn(),
}));

const mockDownload = jest.fn();
const mockGenerateCsv = jest.fn();

jest.mock("export-to-csv", () => ({
  download: () => mockDownload,
  generateCsv: () => mockGenerateCsv,
  mkConfig: jest.fn(),
}));

const { getPapersList } = require("helpers/api");
const { mkConfig } = require("export-to-csv");

describe("ExportButton", () => {
  const mockItems: ISearchItem[] = [
    {
      id: "1",
      paper_id: "1",
      score: 0.5,
      title: "Test Title",
      text: "Test Claim",
      primary_author: "Author1",
      authors: ["Author1", "Author2"],
      year: 2023,
      volume: "",
      pages: "",
      badges: {
        animal_trial: false,
        disputed: {
          reason: "",
          url: "",
        },
        enhanced: false,
        highly_cited_paper: false,
        large_human_trial: false,
        rigorous_journal: false,
        sample_size: undefined,
        study_count: undefined,
        study_type: StudyType.CASE_STUDY,
        very_rigorous_journal: false,
      },
      journal: "Test Journal",
      doi: "Test DOI",
      url_slug: "test-title",
    },
  ];

  beforeEach(() => {
    // Reset all mock implementations before each test
    mockDownload.mockReset();
    mockGenerateCsv.mockReset();
    mkConfig.mockReset();
  });

  it("renders without crashing", () => {
    render(
      <TestProvider>
        <ExportButton items={mockItems} query="Test Query" />
      </TestProvider>
    );
  });

  it("invokes API call on button click", async () => {
    getPapersList.mockResolvedValueOnce({
      paperDetailsListByPaperId: {
        "1": {
          paper: {
            citation_count: 5,
            abstract: "Test Abstract",
            journal: { title: "Journal", scimago_quartile: 1 },
          },
        },
      },
    });

    const { getByText } = render(
      <TestProvider>
        <ExportButton items={mockItems} query="Test Query" />
      </TestProvider>
    );
    fireEvent.click(getByText("Export csv"));

    await waitFor(() => {
      expect(getPapersList).toHaveBeenCalledWith(["1"], {
        includeAbstract: true,
        includeJournal: true,
        enablePaperSearch: false,
      });
    });
  });

  it("handles successful data retrieval and triggers CSV export", async () => {
    getPapersList.mockResolvedValueOnce({
      paperDetailsListByPaperId: {
        "1": {
          id: "1",
          paper_id: "1",
          abstract: "Test Abstract",
          abstract_takeaway: "Test Abstract Takeaway",
          authors: ["Author1", "Author2"],
          badges: {
            animal_trial: false,
            disputed: {
              reason: "",
              url: "",
            },
            enhanced: false,
            highly_cited_paper: false,
            large_human_trial: false,
            rigorous_journal: false,
            sample_size: undefined,
            study_count: undefined,
            study_type: StudyType.CASE_STUDY,
            very_rigorous_journal: false,
          },
          citation_count: 5,
          doi: "Test DOI",
          journal: { title: "Journal", scimago_quartile: 1 },
          pages: "",
          provider_url: "Test provider_url",
          title: "Test Title",
          url_slug: "test-slug",
          volume: "",
          year: 2023,
        },
      },
    });

    const { getByText } = render(
      <TestProvider>
        <ExportButton items={mockItems} query="Test Query" />
      </TestProvider>
    );

    fireEvent.click(getByText("Export csv"));
    await waitFor(() => {
      expect(mockDownload).toHaveBeenCalled();
    });
  });

  it("displays a loading spinner while fetching details", async () => {
    // Mock the API call to delay resolution
    jest.useFakeTimers();

    getPapersList.mockResolvedValueOnce(
      new Promise((resolve) =>
        setTimeout(() => {
          resolve({
            paperDetailsListByPaperId: {
              "1": {
                paper: {
                  citation_count: 5,
                  abstract: "Test Abstract",
                  journal: { title: "Journal", scimago_quartile: 1 },
                },
              },
            },
          });
        }, 100)
      )
    );

    const { getByText, queryByTestId } = render(
      <TestProvider>
        <ExportButton items={mockItems} query="Test Query" />
      </TestProvider>
    );
    fireEvent.click(getByText("Export csv"));
    await waitFor(() => {
      expect(queryByTestId("icon-loader")).toBeInTheDocument();
    });

    jest.runAllTimers();

    await waitFor(() => {
      expect(getPapersList).toHaveBeenCalledWith(["1"], {
        includeAbstract: true,
        includeJournal: true,
        enablePaperSearch: false,
      });
    });

    await waitFor(() => {
      expect(getByText("Export csv")).toBeInTheDocument();
    });
  });
});
