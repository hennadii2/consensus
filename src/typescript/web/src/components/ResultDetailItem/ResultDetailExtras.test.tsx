import { screen } from "@testing-library/react";
import { StudyType } from "helpers/api";
import { renderWithProviders } from "../../__tests__/renderWithProvider";
import ResultDetailExtras from "./ResultDetailExtras";

describe("components/ResultDetailExtras", () => {
  it("should render ResultDetailExtras", () => {
    renderWithProviders(<ResultDetailExtras journal="Hello" />);

    const div = screen.getByTestId("result-detail-extras");

    expect(div).toBeInTheDocument();
  });

  it("should render journal", () => {
    renderWithProviders(<ResultDetailExtras journal="Hello World" />);

    const element = screen.getByTestId("detail-extras-journal");

    expect(element).toHaveTextContent("Hello World");

    const separator = screen.getByTestId("detail-extras-journal-separator");

    expect(separator).toBeInTheDocument();
  });

  it("should render hide journal separator", () => {
    renderWithProviders(<ResultDetailExtras />);

    const separator = screen.queryByTestId("detail-extras-journal-separator");

    expect(separator).not.toBeInTheDocument();
  });

  it("should render author", () => {
    renderWithProviders(<ResultDetailExtras primary_author="Magdalena" />);

    const element = screen.getByTestId("detail-extras-author");

    expect(element).toHaveTextContent("Magdalena et al.");
  });

  it("should render citation", () => {
    renderWithProviders(<ResultDetailExtras citation_count={2} />);

    const element = screen.getByTestId("detail-extras-citation");

    expect(element).toHaveTextContent("2");
  });

  it("should render HightlyCitiedTag", () => {
    Object.defineProperty(document, "cookie", {
      writable: true,
      value: "features=claim-paper-badges",
    });

    renderWithProviders(
      <ResultDetailExtras
        badges={{
          highly_cited_paper: true,
          very_rigorous_journal: false,
          rigorous_journal: false,
          study_type: undefined,
          sample_size: undefined,
          study_count: undefined,
          animal_trial: undefined,
          large_human_trial: undefined,
          disputed: undefined,
          enhanced: false,
        }}
      />
    );

    expect(screen.queryByTestId("highly-cited-tag")).toBeInTheDocument();
    expect(
      screen.queryByTestId("rigorous-journal-tag")
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId("very-rigorous-journal-tag")
    ).not.toBeInTheDocument();
  });

  it("should render VeryRigorousJournalTag", () => {
    Object.defineProperty(document, "cookie", {
      writable: true,
      value: "features=claim-paper-badges",
    });

    renderWithProviders(
      <ResultDetailExtras
        badges={{
          highly_cited_paper: false,
          very_rigorous_journal: true,
          rigorous_journal: false,
          study_type: undefined,
          sample_size: undefined,
          study_count: undefined,
          animal_trial: undefined,
          large_human_trial: undefined,
          disputed: undefined,
          enhanced: false,
        }}
      />
    );

    expect(screen.queryByTestId("highly-cited-tag")).not.toBeInTheDocument();
    expect(
      screen.queryByTestId("rigorous-journal-tag")
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId("very-rigorous-journal-tag")
    ).toBeInTheDocument();
  });

  it("should render RigorousJournalTag", () => {
    Object.defineProperty(document, "cookie", {
      writable: true,
      value: "features=claim-paper-badges",
    });

    renderWithProviders(
      <ResultDetailExtras
        badges={{
          highly_cited_paper: false,
          very_rigorous_journal: false,
          rigorous_journal: true,
          study_type: undefined,
          sample_size: undefined,
          study_count: undefined,
          animal_trial: undefined,
          large_human_trial: undefined,
          disputed: undefined,
          enhanced: false,
        }}
      />
    );

    expect(screen.queryByTestId("highly-cited-tag")).not.toBeInTheDocument();
    expect(screen.queryByTestId("rigorous-journal-tag")).toBeInTheDocument();
    expect(
      screen.queryByTestId("very-rigorous-journal-tag")
    ).not.toBeInTheDocument();
  });

  it("should render StudyTypeTag", () => {
    Object.defineProperty(document, "cookie", {
      writable: true,
      value: "features=enable-study-type",
    });

    renderWithProviders(
      <ResultDetailExtras
        badges={{
          highly_cited_paper: false,
          very_rigorous_journal: false,
          rigorous_journal: false,
          study_type: StudyType.CASE_STUDY,
          sample_size: undefined,
          study_count: undefined,
          animal_trial: undefined,
          large_human_trial: undefined,
          disputed: undefined,
          enhanced: false,
        }}
      />
    );

    expect(screen.queryByTestId("highly-cited-tag")).not.toBeInTheDocument();
    expect(screen.queryByTestId("case-study-tag")).toBeInTheDocument();
    expect(
      screen.queryByTestId("very-rigorous-journal-tag")
    ).not.toBeInTheDocument();
  });

  it("should render RCT", () => {
    Object.defineProperty(document, "cookie", {
      writable: true,
      value: "features=enable-study-type",
    });

    renderWithProviders(
      <ResultDetailExtras
        badges={{
          highly_cited_paper: false,
          very_rigorous_journal: false,
          rigorous_journal: false,
          study_type: StudyType.RCT,
          sample_size: undefined,
          study_count: undefined,
          animal_trial: undefined,
          large_human_trial: undefined,
          disputed: undefined,
          enhanced: false,
        }}
      />
    );

    expect(screen.queryByTestId("highly-cited-tag")).not.toBeInTheDocument();
    expect(screen.queryByTestId("rct-tag")).toBeInTheDocument();
    expect(
      screen.queryByTestId("very-rigorous-journal-tag")
    ).not.toBeInTheDocument();
  });

  it("should render SystematicReview", () => {
    Object.defineProperty(document, "cookie", {
      writable: true,
      value: "features=enable-study-type",
    });

    renderWithProviders(
      <ResultDetailExtras
        badges={{
          highly_cited_paper: false,
          very_rigorous_journal: false,
          rigorous_journal: false,
          study_type: StudyType.SYSTEMATIC_REVIEW,
          sample_size: undefined,
          study_count: undefined,
          animal_trial: undefined,
          large_human_trial: undefined,
          disputed: undefined,
          enhanced: false,
        }}
      />
    );

    expect(screen.queryByTestId("highly-cited-tag")).not.toBeInTheDocument();
    expect(screen.queryByTestId("systematic-review-tag")).toBeInTheDocument();
    expect(
      screen.queryByTestId("very-rigorous-journal-tag")
    ).not.toBeInTheDocument();
  });

  it("should render MetaAnalysis", () => {
    Object.defineProperty(document, "cookie", {
      writable: true,
      value: "features=enable-study-type",
    });

    renderWithProviders(
      <ResultDetailExtras
        badges={{
          highly_cited_paper: false,
          very_rigorous_journal: false,
          rigorous_journal: false,
          study_type: StudyType.META_ANALYSIS,
          sample_size: undefined,
          study_count: undefined,
          animal_trial: undefined,
          large_human_trial: undefined,
          disputed: undefined,
          enhanced: false,
        }}
      />
    );

    expect(screen.queryByTestId("highly-cited-tag")).not.toBeInTheDocument();
    expect(screen.queryByTestId("meta-analysis-tag")).toBeInTheDocument();
    expect(
      screen.queryByTestId("very-rigorous-journal-tag")
    ).not.toBeInTheDocument();
  });

  it("should render DisputedPaperTag", () => {
    renderWithProviders(
      <ResultDetailExtras
        badges={{
          highly_cited_paper: false,
          very_rigorous_journal: false,
          rigorous_journal: false,
          study_type: undefined,
          sample_size: undefined,
          study_count: undefined,
          animal_trial: undefined,
          large_human_trial: undefined,
          disputed: { reason: "test_reason", url: "test_url" },
          enhanced: false,
        }}
      />
    );

    expect(screen.queryByTestId("disputed-paper-tag")).toBeInTheDocument();
  });
});
