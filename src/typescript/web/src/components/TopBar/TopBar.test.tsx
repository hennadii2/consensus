import { render, screen } from "@testing-library/react";
import TopBar from "components/TopBar";
import mockRouter from "next-router-mock";
import TestProvider from "../../__tests__/TestProvider";

jest.mock("next/router", () => require("next-router-mock"));

describe("components/TopBar", () => {
  it("should render topbar", () => {
    // Set the initial url:
    mockRouter.push("/search");

    render(
      <TestProvider>
        <TopBar hasSearch />
      </TestProvider>
    );

    const topbar: HTMLDivElement = screen.getByTestId("topbar");

    expect(topbar).toBeInTheDocument();
  });

  it("should render with logo", () => {
    // Set the initial url:
    mockRouter.push("/search");

    render(
      <TestProvider>
        <TopBar hasSearch />
      </TestProvider>
    );

    const topbarLogo: HTMLImageElement = screen.getByTestId("logo-img");

    expect(topbarLogo).toBeInTheDocument();
  });

  it("should render with search form", () => {
    // Set the initial url:
    mockRouter.push("/search");

    render(
      <TestProvider>
        <TopBar hasSearch />
      </TestProvider>
    );

    const searchForm: HTMLFormElement[] =
      screen.getAllByTestId("search-input-form");
    // array because of mobile responsive. it has two elements

    expect(searchForm[0]).toBeInTheDocument();
  });
});
