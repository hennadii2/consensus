import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SearchInput from "components/SearchInput";
import mockRouter from "next-router-mock";
import TestProvider from "../../__tests__/TestProvider";

jest.mock("next/router", () => require("next-router-mock"));

describe("components/SearchInput", () => {
  it("should be able to enter value", async () => {
    // Set the initial url:
    mockRouter.push("/search");

    render(
      <TestProvider>
        <SearchInput />
      </TestProvider>
    );

    const input: HTMLInputElement = screen.getByTestId("search-input");

    await userEvent.type(input, "test search");
    expect(input.value).toBe("test search");
  });

  it("should be able to render close button", async () => {
    // Set the initial url:
    mockRouter.push("/search");

    render(
      <TestProvider>
        <SearchInput />
      </TestProvider>
    );

    const input: HTMLInputElement = screen.getByTestId("search-input");
    const closeButtonBefore = screen.queryByTestId("close-input");
    expect(closeButtonBefore).not.toBeInTheDocument();

    await userEvent.type(input, "test search");
    const closeButtonAfter = screen.getByTestId("close-input");
    expect(closeButtonAfter).toBeInTheDocument();

    expect(input.value).toBe("test search");
    await userEvent.click(closeButtonAfter);
    expect(input.value).toBe("");
  });
});
