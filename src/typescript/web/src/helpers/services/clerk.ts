import { EmailAddressJSON, UserResource } from "@clerk/types";
import { getDaysBetweenDates, getMinutesBetweenDates } from "helpers/date";

declare global {
  interface Window {
    Clerk: any;
  }
}

// Error message Clerk displays if a user account was not found.
export const COULDNT_FIND_ACCOUNT_MESSAGE = "Couldn't find your account.";
// Number of minutes since last activity that should be considered a new session
const SESSION_LIMIT_MINUTES = 30;

export enum ClerkEvent {
  ERROR_NOT_ALLOWED_ACCESS = "ERROR_NOT_ALLOWED_ACCESS",
  ERROR_COULDNT_FIND_ACCOUNT = "ERROR_COULDNT_FIND_ACCOUNT",
  LOG_IN = "LOG_IN",
  LOG_OUT = "LOG_OUT",
  SIGN_UP = "SIGN_UP",
}

export enum ClerkAuthMethod {
  GOOGLE = "google",
  FACEBOOK = "facebook",
  EMAIL = "email",
}

export interface CustomUserMetadata {
  userAge: number;
  sessions: number;
  searches: number;
  lastActivityAt: string;
}

export function updateUser(
  user: UserResource,
  increaseSearchCount: boolean
): CustomUserMetadata {
  const now = new Date();
  const createdAt = user.createdAt ? new Date(user.createdAt) : now;

  const previousSessions = (user.unsafeMetadata?.sessions || 1) as number;
  const previousSearches = (user?.unsafeMetadata?.searches || 0) as number;
  const previousLastActivityAt = user.unsafeMetadata?.lastActivityAt as string;

  const minutesSinceLastActivity = getMinutesBetweenDates(
    previousLastActivityAt ? new Date(previousLastActivityAt) : new Date(),
    new Date()
  );
  const increaseSessionCount = minutesSinceLastActivity > SESSION_LIMIT_MINUTES;

  const updatedCustomMetadata: CustomUserMetadata = {
    userAge: getDaysBetweenDates(createdAt, now),
    sessions: increaseSessionCount ? previousSessions + 1 : previousSessions,
    searches: increaseSearchCount ? previousSearches + 1 : previousSearches,
    lastActivityAt: now.toISOString(),
  };

  user.update?.({
    unsafeMetadata: {
      ...(user.unsafeMetadata || {}),
      ...updatedCustomMetadata,
    },
  });

  return updatedCustomMetadata;
}

export async function initEventHandler(
  onClerkEventCallback: (action: any, response: any) => void
) {
  // wait one second so window.Clerk has been initiated
  await new Promise((r) => setTimeout(r, 1000));
  if (window.Clerk) {
    window.Clerk.__unstable__onAfterResponse(
      async (action: any, response: any) => {
        onClerkEventCallback(action, response);
      }
    );
  }
}

export function isOauthMethod(authMethod: ClerkAuthMethod): boolean {
  return (
    authMethod === ClerkAuthMethod.GOOGLE ||
    authMethod === ClerkAuthMethod.FACEBOOK
  );
}

export function identifyAuthMethod(action: any): ClerkAuthMethod | undefined {
  if (action.body?.includes("strategy=oauth_google")) {
    return ClerkAuthMethod.GOOGLE;
  }
  if (action.body?.includes("strategy=oauth_facebook")) {
    return ClerkAuthMethod.FACEBOOK;
  }
  if (
    action.body?.includes("strategy=password") ||
    action.body?.includes("strategy=email_link") ||
    action.body?.includes("email_address") ||
    action.body?.includes("identifier")
  ) {
    return ClerkAuthMethod.EMAIL;
  }
  return undefined;
}

export function identifyAuthMethodFromEmailAddresses(
  emailAddresses: EmailAddressJSON[]
): ClerkAuthMethod | undefined {
  const verifiedAccounts = emailAddresses.filter(
    (x) => x?.verification?.status == "verified"
  );
  if (!verifiedAccounts.length) {
    return undefined;
  }
  const account = verifiedAccounts[0];
  if (account.verification?.strategy == "email_link") {
    return ClerkAuthMethod.EMAIL;
  } else if (account.verification?.strategy == "from_oauth_google") {
    return ClerkAuthMethod.GOOGLE;
  } else if (account.verification?.strategy == "from_oauth_facebook") {
    return ClerkAuthMethod.FACEBOOK;
  } else {
    console.error(`UNKNOWN OAUTH PROVIDER: {account.provider}`);
  }
  return undefined;
}

export function identifyEvent(
  action: any,
  response: any
): ClerkEvent | undefined {
  if (response.status >= 400 && response.status <= 499) {
    const errors: any[] = response.payload.errors || [];
    for (const err of errors) {
      if (err?.code === "not_allowed_access") {
        return ClerkEvent.ERROR_NOT_ALLOWED_ACCESS;
      }

      if (err?.message === COULDNT_FIND_ACCOUNT_MESSAGE) {
        // TODO: look at this one megan
        return ClerkEvent.ERROR_COULDNT_FIND_ACCOUNT;
      }
    }
  }
  if (action.method === "DELETE" && action.path === "/client" && response.ok) {
    return ClerkEvent.LOG_OUT;
  }
  if (
    action.method === "POST" &&
    action.path?.includes("/client/sign_ins") &&
    response.ok
  ) {
    return ClerkEvent.LOG_IN;
  }
  if (
    action.method === "POST" &&
    action.path === "/client/sign_ups" &&
    response.ok
  ) {
    return ClerkEvent.SIGN_UP;
  }
  return undefined;
}

export function isTransfer(action: any): boolean {
  return action.body.includes("transfer=true");
}
