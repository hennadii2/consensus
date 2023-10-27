import { render, screen } from "@testing-library/react";
import Page from "../pages/sign-up";
import TestProvider from "./TestProvider";

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

describe("pages/index", () => {
  it("should render", () => {
    render(
      <TestProvider>
        <Page />
      </TestProvider>
    );

    const paragraph: HTMLParagraphElement = screen.getByTestId("sign-up");

    expect(paragraph).toBeInTheDocument();
  });

  it("should render auth message", () => {
    render(
      <TestProvider>
        <Page />
      </TestProvider>
    );

    const paragraph: HTMLParagraphElement = screen.getByTestId("auth-message");

    expect(paragraph).toBeInTheDocument();
  });
});
