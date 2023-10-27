import { SignedOut, SignIn, useAuth } from "@clerk/nextjs";
import AuthMessage from "components/AuthMessage";
import Head from "components/Head";
import path from "constants/path";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import { useRouter } from "next/router";
import { useEffect } from "react";

export default function SignInPage() {
  const [pageLabels] = useLabels("screens.sign-in");

  const { replace, asPath } = useRouter();
  const { isLoaded, isSignedIn } = useAuth();

  const isMobile = useAppSelector((state) => state.setting.isMobile);

  const isFromSearch = asPath.includes("results");
  useEffect(() => {
    if (isLoaded && isSignedIn) {
      replace(path.SEARCH);
    }
  }, [isLoaded, isSignedIn, replace]);

  return (
    <>
      <Head
        title={pageLabels["title"]}
        description={pageLabels["description"]}
      />
      <div
        data-testid="sign-in"
        className="container max-w-6xl m-auto grid grid-cols-1  md:-mt-10 mb-20"
      >
        {isFromSearch && (
          <div>
            <h1 className="text-[2rem] font-bold text-center -mt-2">
              {pageLabels["sign-in-first"]}
            </h1>
            <p
              className="text-base text-gray-600 text-center mb-6"
              dangerouslySetInnerHTML={{
                __html: pageLabels["sign-in-first-desc"].replace(
                  "SIGN_UP_URL",
                  path.SIGN_UP
                ),
              }}
            ></p>
          </div>
        )}
        <div className="md:-mt-2">
          <AuthMessage />
        </div>
        <SignedOut>
          <div className="m-auto">
            <SignIn
              path={path.SIGN_IN}
              signUpUrl={path.SIGN_UP}
              redirectUrl={path.SEARCH}
              appearance={{
                variables: {
                  fontSize: isMobile ? "1rem" : "1.334rem",
                },
              }}
            />
          </div>
        </SignedOut>
      </div>
    </>
  );
}
