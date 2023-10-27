import { SignedOut, SignUp, useAuth } from "@clerk/nextjs";
import AuthMessage from "components/AuthMessage";
import Head from "components/Head";
import {
  PRIVACY_PAGE_URL,
  SUPPORT_EMAIL,
  TERMS_PAGE_URL,
} from "constants/config";
import path from "constants/path";
import { SynthesizeToggleState } from "enums/meter";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { setCookie } from "react-use-cookie";

export default function SignUpPage() {
  const { replace, events } = useRouter();
  const { isLoaded, isSignedIn } = useAuth();
  const [pageLabels] = useLabels("screens.sign-up");

  const [isVerifyEmail, setIsVerifyEmail] = useState(false);

  const isMobile = useAppSelector((state) => state.setting.isMobile);

  useEffect(() => {
    setCookie("synthesize", SynthesizeToggleState.ON);
  }, []);

  useEffect(() => {
    const onhashChange = (event: any) => {
      setIsVerifyEmail(event.newURL.includes("verify-email-address"));
    };

    window.addEventListener("hashchange", onhashChange);

    return () => {
      window.removeEventListener("hashchange", onhashChange);
    };
  }, [events]);

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
        data-testid="sign-up"
        className="container max-w-6xl m-auto grid grid-cols-1 mb-20"
      >
        <div className="md:-mt-12">
          <AuthMessage />
        </div>
        <SignedOut>
          <div className="mx-auto">
            <SignUp
              path={path.SIGN_UP}
              redirectUrl={path.SEARCH}
              signInUrl={path.SIGN_IN}
              appearance={{
                layout: {
                  showOptionalFields: true,
                  privacyPageUrl: PRIVACY_PAGE_URL,
                  termsPageUrl: TERMS_PAGE_URL,
                },
                variables: {
                  fontSize: isMobile ? "1rem" : "1.334rem",
                },
              }}
            />
          </div>
          {isVerifyEmail && (
            <div className="max-w-lg m-auto mt-10 text-center">
              <p
                dangerouslySetInnerHTML={{
                  __html: pageLabels["verify-message"].replaceAll(
                    "SUPPORT_EMAIL",
                    SUPPORT_EMAIL
                  ),
                }}
              ></p>
            </div>
          )}
        </SignedOut>
      </div>
    </>
  );
}
