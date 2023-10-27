import { render } from "@testing-library/react";
import React, { PropsWithChildren } from "react";
import TestProvider from "./TestProvider";

export function renderWithProviders(ui: React.ReactElement) {
  function Wrapper({ children }: PropsWithChildren<{}>): JSX.Element {
    return <TestProvider>{children}</TestProvider>;
  }
  return { ...render(ui, { wrapper: Wrapper }) };
}
