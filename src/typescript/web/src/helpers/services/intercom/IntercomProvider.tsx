import { useRouter } from "next/router";
import { useEffect } from "react";
import {
  boot as bootIntercom,
  load as loadIntercom,
  update as updateIntercom,
} from "./index";

interface IntercomProviderProps {
  children: React.ReactNode;
  enabled?: boolean;
}

export const IntercomProvider: React.FC<IntercomProviderProps> = ({
  children,
  enabled,
}) => {
  const router = useRouter();

  if (enabled && typeof window !== "undefined") {
    loadIntercom();
    bootIntercom();
  }

  useEffect(() => {
    const handleRouteChange = (url: string) => {
      if (enabled && typeof window !== "undefined") {
        updateIntercom();
      }
    };

    router.events.on("routeChangeStart", handleRouteChange);

    // If the component is unmounted, unsubscribe
    // from the event with the `off` method:
    return () => {
      router.events.off("routeChangeStart", handleRouteChange);
    };
  }, [router.events, enabled]);

  return <>{children}</>;
};
