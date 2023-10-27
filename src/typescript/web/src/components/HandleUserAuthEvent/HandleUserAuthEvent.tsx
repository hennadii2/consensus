/* eslint-disable react-hooks/exhaustive-deps */
import { useAuth, useUser } from "@clerk/nextjs";
import Modal from "components/Modal";
import { SEARCH_ITEM, WAITLIST_URL } from "constants/config";
import path from "constants/path";
import { generateHmac } from "helpers/generateHmac";
import * as clerk from "helpers/services/clerk";
import {
  boot as bootIntercom,
  shutdown as shutdownIntercom,
  update as updateIntercom,
} from "helpers/services/intercom";
import useAnalytics from "hooks/useAnalytics";
import useLabels from "hooks/useLabels";
import { useAppSelector } from "hooks/useStore";
import Link from "next/link";
import { useRouter } from "next/router";
import React, { useEffect, useMemo, useState } from "react";

const LOGIN_METHOD_ITEM = "login_method";
const SIGNUP_METHOD_ITEM = "signup_method";
const OAUTH_METHOD_ITEM = "oauth_method";

/**
 * @component HandleUserAuthEvent
 * @description component handle error from clerk.
 * @example
 * return (
 *   <HandleUserAuthEvent />
 * )
 */

const HandleUserAuthEvent = () => {
  const [errorLabel] = useLabels("error");
  const { setAnalyticUser, loginEvent, logoutEvent, signupEvent, searchEvent } =
    useAnalytics();
  const { route, query } = useRouter();
  const [open, setOpen] = useState(false);
  const { user } = useUser();
  const { isSignedIn } = useAuth();
  const isUserLoaded = typeof user?.update === "function";
  const hasSubscription = useAppSelector((state) =>
    Boolean(
      state.subscription.subscription.user ||
        state.subscription.subscription.org
    )
  );
  const subscriptionInterval = useAppSelector(
    (state) => state.subscription.subscription.user?.plan.interval
  );

  const billingPeriod = useMemo(() => {
    if (!hasSubscription) {
      return;
    }
    if (subscriptionInterval === "year") {
      return "Annually";
    }
    if (subscriptionInterval === "month") {
      return "Monthly";
    }
    return;
  }, [subscriptionInterval, hasSubscription]);

  // on every search or page change, update the user across all services
  useEffect(() => {
    if (user && isUserLoaded) {
      const isNewSearch = false;
      const updatedMetadata = clerk.updateUser(user, isNewSearch);
    }
  }, [isUserLoaded, route, query]);

  // on every page reload, try record auth events
  useEffect(() => {
    if (user && isUserLoaded && isSignedIn) {
      const userCreatedAt =
        typeof user.createdAt === "number"
          ? new Date(user.createdAt)
          : user.createdAt;
      const hash = generateHmac(user.id);
      updateIntercom({
        name: user.fullName,
        email: user.primaryEmailAddress?.emailAddress,
        created_at: userCreatedAt,
        user_id: user.id,
        user_hash: hash,
        Plan: hasSubscription ? "Premium" : "Free",
        "Billing Period": billingPeriod,
      });
      setAnalyticUser(user);

      const loginMethod = localStorage.getItem(LOGIN_METHOD_ITEM);
      if (loginMethod) {
        loginEvent(loginMethod);
        localStorage.removeItem(LOGIN_METHOD_ITEM);
        localStorage.removeItem(OAUTH_METHOD_ITEM);
      }

      const signupMethod = localStorage.getItem(SIGNUP_METHOD_ITEM);
      if (signupMethod) {
        signupEvent(signupMethod);
        localStorage.removeItem(SIGNUP_METHOD_ITEM);
        localStorage.removeItem(OAUTH_METHOD_ITEM);
      }

      const searchItem = localStorage.getItem(SEARCH_ITEM);
      if (searchItem) {
        searchEvent(searchItem);
        localStorage.removeItem(SEARCH_ITEM);
      }
    }
  }, [
    isUserLoaded,
    user?.id,
    setAnalyticUser,
    searchEvent,
    signupEvent,
    loginEvent,
    isSignedIn,
    hasSubscription,
    billingPeriod,
  ]);

  // on every page change, check if we should delete data in local storage if
  // we are canceling the signin or signup process
  useEffect(() => {
    const hash = typeof window === "undefined" ? "" : window?.location?.hash;
    if (
      [path.SIGN_IN, path.SIGN_UP].includes(route) &&
      !hash.includes("verify")
    ) {
      localStorage.removeItem(SIGNUP_METHOD_ITEM);
      localStorage.removeItem(LOGIN_METHOD_ITEM);
    }

    if (route === "/") {
      localStorage.removeItem(SEARCH_ITEM);
    }
  }, [route]);

  // register callbacks for handling all clerk events
  useEffect(() => {
    clerk.initEventHandler((action: any, response: any) => {
      const clerkEvent = clerk.identifyEvent(action, response);
      switch (clerkEvent) {
        case clerk.ClerkEvent.ERROR_NOT_ALLOWED_ACCESS: {
          setOpen(true);
          break;
        }
        case clerk.ClerkEvent.ERROR_COULDNT_FIND_ACCOUNT: {
          setTimeout(() => {
            // replace error message message with custom text
            const element = document.getElementById("error-identifier");
            if (
              element &&
              element.innerHTML === clerk.COULDNT_FIND_ACCOUNT_MESSAGE
            ) {
              element.innerHTML = errorLabel["couldnt-find-account"];
            }
          }, 100);
          break;
        }
        case clerk.ClerkEvent.LOG_OUT: {
          const user = response.payload?.response?.sessions?.[0]?.user;
          if (user) {
            logoutEvent();
            shutdownIntercom();
            bootIntercom();
          }
          break;
        }
        case clerk.ClerkEvent.LOG_IN: {
          const authMethod = clerk.identifyAuthMethod(action);
          if (authMethod) {
            localStorage.setItem(LOGIN_METHOD_ITEM, authMethod);
            if (clerk.isOauthMethod(authMethod)) {
              localStorage.setItem(OAUTH_METHOD_ITEM, authMethod);
            }
          }
          break;
        }
        case clerk.ClerkEvent.SIGN_UP: {
          const authMethod = clerk.identifyAuthMethod(action);
          if (authMethod) {
            localStorage.setItem(SIGNUP_METHOD_ITEM, authMethod);
            if (clerk.isOauthMethod(authMethod)) {
              localStorage.setItem(OAUTH_METHOD_ITEM, authMethod);
            }
          }
          if (clerk.isTransfer(action)) {
            const oauth = localStorage.getItem(OAUTH_METHOD_ITEM);
            if (oauth) {
              localStorage.setItem(SIGNUP_METHOD_ITEM, oauth);
            }
          }
          break;
        }
      }
    });
  }, []);

  return (
    <Modal
      open={open}
      onClose={() => setOpen(false)}
      title={errorLabel["warning"]}
    >
      <p className="text-base mt-3 text-gray-700">
        {errorLabel["unregistered-beta"]}{" "}
        <Link href={WAITLIST_URL} passHref legacyBehavior>
          <a className="text-blue-600 font-bold underline">
            {errorLabel["signup-waitlist"]}
          </a>
        </Link>{" "}
        {errorLabel["or-try"]}.
      </p>
    </Modal>
  );
};

export default HandleUserAuthEvent;
