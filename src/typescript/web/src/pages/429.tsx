import { useAuth } from "@clerk/nextjs";
import Button from "components/Button";
import Head from "components/Head";
import { SUPPORT_EMAIL } from "constants/config";
import path from "constants/path";
import useLabels from "hooks/useLabels";
import Link from "next/link";

export default function TooManyRequest() {
  const [pageLabels] = useLabels("screens.too-many-requests");
  const { isSignedIn, isLoaded } = useAuth();
  const message = isSignedIn
    ? pageLabels["message-auth"]
    : pageLabels["message"];
  const description = isSignedIn
    ? pageLabels["description-auth"]
    : pageLabels["description"];

  return (
    <>
      <Head title={pageLabels["title"]} />
      {isLoaded ? (
        <>
          {isSignedIn ? (
            <div className="container max-w-4xl m-auto grid grid-cols-1 md:grid-cols-2 pt-4 md:pt-16 text-center md:text-left mb-20">
              <div>
                <div className="block md:hidden mx-16 mt-6">
                  <img alt="servererror" src="/images/too-many-request.svg" />
                </div>
                <h1 className="text-[27px] md:text-4xl leading-8 font-bold text-[#085394] mt-6 md:mt-12">
                  {message}
                </h1>
                <p
                  dangerouslySetInnerHTML={{
                    __html: description.replaceAll(
                      "SUPPORT_EMAIL",
                      SUPPORT_EMAIL
                    ),
                  }}
                  className={`text-gray-900 mt-2 md:mt-20 max-w-[391px]`}
                ></p>
              </div>
              <div className=" justify-center hidden md:flex">
                <img alt="servererror" src="/images/too-many-request.svg" />
              </div>
            </div>
          ) : (
            <div className="flex flex-1 items-center flex-col">
              <h1 className="text-[22px] md:text-[32px] leading-[33px] md:leading-[48px] font-bold text-[#222F2B] mt-10 md:mt-20">
                {message}
              </h1>
              <p
                className={`text-black mt-3 md:mt-[6px] text-lg md:text-xl max-w-[333px] md:max-w-[552px] text-center`}
              >
                {description}
              </p>
              <div className="flex flex-col md:flex-row mt-10 w-full md:w-auto gap-y-4 md:gap-x-4 md:gap-y-0 px-[21px]">
                <Link href={path.SIGN_IN} passHref legacyBehavior>
                  <a>
                    <Button
                      className="text-center justify-center w-full md:w-[140px] h-12"
                      variant="secondary"
                    >
                      Login
                    </Button>
                  </a>
                </Link>
                <Link href={path.SIGN_UP} passHref legacyBehavior>
                  <a>
                    <Button
                      className="text-center justify-center w-full md:w-[140px] h-12"
                      variant="primary"
                    >
                      Sign Up
                    </Button>
                  </a>
                </Link>
              </div>
              <p
                dangerouslySetInnerHTML={{
                  __html: pageLabels["description-auth2"].replaceAll(
                    "SUPPORT_EMAIL",
                    SUPPORT_EMAIL
                  ),
                }}
                className={`text-[#688092] text-center leading-6 mt-[26px] max-w-[333px] md:max-w-[445px]`}
              ></p>
            </div>
          )}
        </>
      ) : null}
    </>
  );
}
