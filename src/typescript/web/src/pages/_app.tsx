import { ClerkProvider } from "@clerk/nextjs";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Footer from "components/Footer";
import HandleAnalytic from "components/HandleAnalytic";
import HandleUserAuthEvent from "components/HandleUserAuthEvent";
import { SubscriptionProvider } from "components/Subscription";
import TopBar from "components/TopBar";
import path from "constants/path";
import { FeatureFlag } from "enums/feature-flag";
import { IntercomProvider } from "helpers/services/intercom/IntercomProvider";
import * as mixpanel from "helpers/services/mixpanel";
import useIsFeatureEnabled from "hooks/useIsFeatureEnabled";
import useLabels from "hooks/useLabels";
import type { AppContext, AppProps } from "next/app";
import Head from "next/head";
import { useRouter } from "next/router";
import Script from "next/script";
import { useEffect } from "react";
import { Provider } from "react-redux";
import { store } from "store";
import "styles/clerk.css";
import "styles/globals.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: Infinity,
    },
  },
});

type MyAppProps = AppProps & {};

/**
 * @description Wrapper component to all of the pages.
 */
const MyApp = ({ Component, pageProps }: MyAppProps) => {
  const [pageTitle] = useLabels("page-title");
  const { pathname } = useRouter();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const features = {
    bookmarkEnabled: useIsFeatureEnabled(FeatureFlag.BOOKMARK),
  };

  const hideSearch = ["/", path.SIGN_IN, path.SIGN_UP].includes(pathname);
  const hideHelp = [path.SIGN_IN, path.SIGN_UP].includes(pathname);
  const hideBookmarkButton = [path.SIGN_IN, path.SIGN_UP].includes(pathname);

  // Initialize services
  useEffect(() => {
    mixpanel.initialize();
  }, []);

  return (
    <IntercomProvider enabled={true}>
      <SubscriptionProvider>
        <ClerkProvider
          {...pageProps}
          appearance={{
            variables: {
              fontSize: "1.334rem",
            },
          }}
        >
          <QueryClientProvider client={queryClient}>
            <Provider store={store}>
              <Head>
                <title>{pageTitle}</title>
                <meta property="og:title" content="Consensus" key="og:title" />
                <meta name="robots" content="all" />
                <link rel="icon" type="image/png" href="/favicon.png" />
              </Head>
              <Script
                id="gtm-script"
                strategy="afterInteractive"
              >{`(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
                      new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
                      j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
                      'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
                      })(window,document,'script','dataLayer','${process.env.NEXT_PUBLIC_GOOGLE_TAG_MANAGER_ID}');`}</Script>
              <Script src="https://js.stripe.com/v3" async></Script>
              <div className={pageProps.pathname.replaceAll("/", "")}>
                <HandleAnalytic />
                <HandleUserAuthEvent />
                <div
                  className={`container py-4 ${
                    hideSearch ? "" : "sticky top-0 z-40 bg-[#EAFAF5]"
                  }`}
                >
                  <TopBar
                    hasSearch={!hideSearch}
                    hasHelp={!hideHelp}
                    hasBookmark={
                      !hideBookmarkButton && features.bookmarkEnabled
                    }
                  />
                </div>
                <div
                  style={{
                    minHeight: "calc(100vh - 380px)",
                  }}
                >
                  <Component {...pageProps} />
                </div>
                <Footer />
              </div>
            </Provider>
          </QueryClientProvider>
        </ClerkProvider>
      </SubscriptionProvider>
    </IntercomProvider>
  );
};

MyApp.getInitialProps = async ({ Component, ctx }: AppContext) => {
  let pageProps: any = {};

  if (Component.getInitialProps) {
    pageProps = await Component.getInitialProps(ctx);
  }

  pageProps.pathname = ctx.pathname;

  return { pageProps };
};

export default MyApp;
