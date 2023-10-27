import type { ReactNode } from "react";
import { SWRConfig } from "swr";

export const changePaymentMethodUrl_suffix =
  "update-payment-method/changePaymentMethodFromHome";
export const subscriptionReactivateUrl_suffix = "reactivate";
export const SubscriptionProvider = ({ children }: { children: ReactNode }) => {
  return (
    <SWRConfig
      value={{
        fetcher: async (args) => {
          const data = await fetch(args);
          return await data.json();
        },
      }}
    >
      {children}
    </SWRConfig>
  );
};

export interface redirectToCheckoutArgs {
  price: string;
  successUrl?: string;
  cancelUrl?: string;
  discountId?: string;
}

export interface redirectToCustomerPortalArgs {
  returnUrl?: string;
}

export interface redirectToCustomerPortalSubscriptionCancelArgs {
  returnUrl?: string;
  subscription?: string;
}

export interface redirectToCustomerPortalSubscriptionUpdateArgs {
  returnUrl?: string;
  subscription?: string;
}

export interface redirectToCustomerPortalPaymentMethodManagementArgs {
  subscriptionId: string;
  returnUrl?: string;
}

export interface redirectToCustomerPortalSubscriptionReactivateArgs {
  subscriptionId: string;
  returnUrl?: string;
}

export function useSubscription() {
  const endpoint = "/api/subscription";
  const redirectToCheckout = async (args: redirectToCheckoutArgs) => {
    if (!args.successUrl) {
      args.successUrl = window.location.href;
    }
    if (!args.cancelUrl) {
      args.cancelUrl = window.location.href;
    }
    const sessionResponse = await fetch(
      `${endpoint}?action=redirectToCheckout`,
      {
        method: "post",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(args),
      }
    );
    const session = await sessionResponse.json();
    window.location.href = session.url;
  };

  const redirectToCustomerPortal = async (
    args: redirectToCustomerPortalArgs
  ) => {
    args = args || {};
    if (!args.returnUrl) {
      args.returnUrl = window.location.href;
    }
    const sessionResponse = await fetch(
      `${endpoint}?action=redirectToCustomerPortal`,
      {
        method: "post",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(args),
      }
    );
    const session = await sessionResponse.json();
    window.location.href = session.url;
  };

  const redirectToCustomerPortalSubscriptionCancel = async (
    args: redirectToCustomerPortalSubscriptionCancelArgs
  ) => {
    args = args || {};
    if (!args.returnUrl) {
      args.returnUrl = window.location.href;
    }
    if (!args.subscription) {
      args.subscription = "empty";
    }
    const sessionResponse = await fetch(
      `${endpoint}?action=redirectToCustomerPortalSubscriptionCancel`,
      {
        method: "post",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(args),
      }
    );
    const session = await sessionResponse.json();
    window.location.href = session.url;
  };

  const redirectToCustomerPortalSubscriptionUpdate = async (
    args: redirectToCustomerPortalSubscriptionUpdateArgs
  ) => {
    args = args || {};
    if (!args.returnUrl) {
      args.returnUrl = window.location.href;
    }
    if (!args.subscription) {
      args.subscription = "empty";
    }
    const sessionResponse = await fetch(
      `${endpoint}?action=redirectToCustomerPortalSubscriptionUpdate`,
      {
        method: "post",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(args),
      }
    );
    const session = await sessionResponse.json();
    window.location.href = session.url;
  };

  const redirectToCustomerPortalPaymentMethodManagement = async (
    args: redirectToCustomerPortalPaymentMethodManagementArgs
  ) => {
    args = args || {};
    if (!args.returnUrl) {
      args.returnUrl = window.location.href;
    }
    const sessionResponse = await fetch(
      `${endpoint}?action=redirectToCustomerPortal`,
      {
        method: "post",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(args),
      }
    );
    const session = await sessionResponse.json();
    window.location.href =
      session.url +
      "/subscriptions/" +
      args.subscriptionId +
      "/" +
      changePaymentMethodUrl_suffix;
  };

  const redirectToCustomerPortalSubscriptionReactivate = async (
    args: redirectToCustomerPortalSubscriptionReactivateArgs
  ) => {
    args = args || {};
    if (!args.returnUrl) {
      args.returnUrl = window.location.href;
    }
    const sessionResponse = await fetch(
      `${endpoint}?action=redirectToCustomerPortal`,
      {
        method: "post",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(args),
      }
    );
    const session = await sessionResponse.json();
    window.location.href =
      session.url +
      "/subscriptions/" +
      args.subscriptionId +
      "/" +
      subscriptionReactivateUrl_suffix;
  };

  return {
    redirectToCheckout,
    redirectToCustomerPortal,
    redirectToCustomerPortalSubscriptionCancel,
    redirectToCustomerPortalSubscriptionUpdate,
    redirectToCustomerPortalPaymentMethodManagement,
    redirectToCustomerPortalSubscriptionReactivate,
  };
}
