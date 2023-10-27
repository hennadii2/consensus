import { screen } from "@testing-library/react";
import { renderWithProviders } from "../../__tests__/renderWithProvider";
import StudySnapshotResult from "./StudySnapshotResult";

describe("components/StudySnapshot/StudySnapshotResult", () => {
  it("should render StudySnapshotResult(unlocked)", () => {
    renderWithProviders(
      <StudySnapshotResult
        isLocked={false}
        isLoading={false}
        methods={"methods"}
        population={"population"}
        outcomes={"outcomes"}
        sampleSize={10}
      />
    );

    const populationText: HTMLElement = screen.getByTestId("population-text");
    expect(populationText).toHaveTextContent("population");

    const sampleSizeText: HTMLElement = screen.getByTestId("sample-size-text");
    expect(sampleSizeText).toHaveTextContent("10");

    const methodText: HTMLElement = screen.getByTestId("methods-text");
    expect(methodText).toHaveTextContent("methods");

    const outcomesText: HTMLElement = screen.getByTestId("outcomes-text");
    expect(outcomesText).toHaveTextContent("outcomes");
  });

  it("should render StudySnapshotResult(locked)", () => {
    renderWithProviders(
      <StudySnapshotResult
        isLocked={true}
        isLoading={false}
        methods={"methods"}
        population={"population"}
        outcomes={"outcomes"}
        sampleSize={0}
      />
    );

    const populationText: HTMLElement = screen.getByTestId("population-text");
    expect(populationText).toHaveTextContent("Older adults (50-71 years)");

    const sampleSizeText: HTMLElement = screen.getByTestId("sample-size-text");
    expect(sampleSizeText).toHaveTextContent("24");

    const methodText: HTMLElement = screen.getByTestId("methods-text");
    expect(methodText).toHaveTextContent("Observational");

    const outcomesText: HTMLElement = screen.getByTestId("outcomes-text");
    expect(outcomesText).toHaveTextContent(
      "memory, task performance, visual performance, completely randomized block design experiment"
    );
  });

  it("should render StudySnapshotResult(loading)", () => {
    renderWithProviders(
      <StudySnapshotResult
        isLocked={false}
        isLoading={true}
        methods={"methods"}
        population={"population"}
        outcomes={"outcomes"}
        sampleSize={24}
      />
    );

    const populationText: HTMLElement = screen.getByTestId("population-text");
    expect(populationText).toHaveTextContent("");

    const sampleSizeText: HTMLElement = screen.getByTestId("sample-size-text");
    expect(sampleSizeText).toHaveTextContent("");

    const methodText: HTMLElement = screen.getByTestId("methods-text");
    expect(methodText).toHaveTextContent("");

    const outcomesText: HTMLElement = screen.getByTestId("outcomes-text");
    expect(outcomesText).toHaveTextContent("");

    const loadingWidgets: HTMLElement[] = screen.getAllByTestId(
      "study-snapshot-loading"
    );
    expect(loadingWidgets[0]).toBeInTheDocument();
  });
});
