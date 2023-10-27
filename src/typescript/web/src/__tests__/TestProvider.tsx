import { ClerkProvider } from "@clerk/clerk-react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { Provider } from "react-redux";
import { store } from "../store";

const queryClient = new QueryClient();
export interface TestProviderProps {
  children: React.ReactNode;
}

function TestProvider({ children }: TestProviderProps) {
  return (
    <ClerkProvider
      frontendApi={process.env.NEXT_PUBLIC_CLERK_FRONTEND_API ?? ""}
    >
      <QueryClientProvider client={queryClient}>
        <Provider store={store}>{children}</Provider>
      </QueryClientProvider>
    </ClerkProvider>
  );
}

export default TestProvider;
