import { useRouter } from "next/router";
import { useEffect } from "react";

/**
 * @hook useDevelopmentComponent
 * @description Removed the access to production and redirects to main page.
 * @example
 * useDevelopmentComponent();
 */
const useDevelopmentComponent = () => {
  const router = useRouter();

  return useEffect(() => {
    if (process.env.NODE_ENV !== "development") {
      router.push("/");
    }
  }, [router]);
};

export default useDevelopmentComponent;
