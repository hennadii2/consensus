import useAnalytics from "hooks/useAnalytics";
import { useRouter } from "next/router";
import React, { useEffect } from "react";

function HandleAnalytic() {
  const { route } = useRouter();
  const { pageViewEvent } = useAnalytics();

  useEffect(() => {
    pageViewEvent({ route, pageTitle: document.title });
  }, [route, pageViewEvent]);

  return <div />;
}

export default HandleAnalytic;
