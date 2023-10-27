import { clerkClient } from "@clerk/nextjs/server";
import { CLERK_META_KEY_STRIPE_CUSTOMER_ID } from "constants/config";
import { getSubscriptionProductsAPI } from "helpers/api";
import Stripe from "stripe";
import { getActiveSubscription } from "./subscription";

export const stripeApiClient = new Stripe(
  process.env.STRIPE_SECRET_KEY as string,
  {
    apiVersion: "2022-11-15",
  }
);

export interface PaymentDetailResponse {
  type: string;
  card: {
    brand: string;
    last4: string;
    exp_month: number;
    exp_year: number;
  };
}

export const findStripeCustomerId = async ({
  clerkUserId,
  createIfNotExist,
}: {
  clerkUserId: string;
  createIfNotExist: boolean;
}) => {
  const user = await clerkClient.users.getUser(clerkUserId);
  if (user.publicMetadata[CLERK_META_KEY_STRIPE_CUSTOMER_ID]) {
    return user.publicMetadata[CLERK_META_KEY_STRIPE_CUSTOMER_ID] as string;
  }

  if (createIfNotExist) {
    const userEmail = user.emailAddresses.find(
      (x: any) => x.id === user.primaryEmailAddressId
    )?.emailAddress;

    let customerId: string = "";
    try {
      const customers = await stripeApiClient.customers.list({
        email: userEmail,
        limit: 1,
      });
      if (customers.data.length > 0) {
        customerId = customers.data[0].id as string;
      }
    } catch (error) {
      console.error(error);
    }

    if (customerId == "") {
      const customerCreate = await stripeApiClient.customers.create(
        {
          name: user.firstName + " " + user.lastName,
          email: userEmail,
          metadata: {
            clerkUserId: user.id,
          },
        },
        {
          idempotencyKey: user.id,
        }
      );
      customerId = customerCreate.id;
    }

    let publicMetaData = user.publicMetadata;
    publicMetaData[CLERK_META_KEY_STRIPE_CUSTOMER_ID] = customerId;

    const userRet = await clerkClient.users.updateUser(user.id, {
      publicMetadata: publicMetaData,
    });
    return userRet.publicMetadata[CLERK_META_KEY_STRIPE_CUSTOMER_ID] as string;
  }

  return null;
};

export const customerHasFeature = async ({
  customerId,
  feature,
  headerData,
}: {
  customerId: string;
  feature: string;
  headerData?: any;
}) => {
  let subscriptionProduct = null;
  try {
    const subscription = await getActiveSubscription({
      customerId: customerId,
      headerData: headerData,
    });

    if (subscription.user) {
      const subscriptoinProducts = await getSubscriptionProductsAPI(
        subscription.user.plan.product,
        headerData
      );
      if (subscriptoinProducts.subscription_products.length > 0) {
        subscriptionProduct =
          subscriptoinProducts.subscription_products[0].product_data;
      }
    }
  } catch (error) {
    subscriptionProduct = null;
  }

  if (subscriptionProduct) {
    let features = "";
    if (subscriptionProduct.metadata.hasOwnProperty("features")) {
      features = subscriptionProduct.metadata.features;
    }

    const splittedFeatures = features?.split(",");
    if (splittedFeatures.includes(feature)) {
      return true;
    }
  }
  return false;
};

export const cancelSubscription = async ({
  customerId,
}: {
  customerId: string;
}) => {
  const subscription = await getActiveSubscription({ customerId });

  if (subscription.user) {
    const retSubscription = await stripeApiClient.subscriptions.del(
      subscription.user.id
    );
    if (retSubscription?.canceled_at) {
      return true;
    }
  }

  return false;
};

export const convertPaymentMethodToResponseObject = ({
  paymentMethod,
}: {
  paymentMethod: Stripe.PaymentMethod;
}): PaymentDetailResponse => {
  let detailResponse: PaymentDetailResponse = {
    type: "",
    card: {
      brand: "",
      exp_month: 0,
      exp_year: 0,
      last4: "",
    },
  };

  detailResponse.type = paymentMethod.type;
  if (paymentMethod.type == "card" && paymentMethod.card) {
    detailResponse.card.brand = paymentMethod.card.brand;
    detailResponse.card.exp_month = paymentMethod.card.exp_month;
    detailResponse.card.exp_year = paymentMethod.card.exp_year;
    detailResponse.card.last4 = paymentMethod.card.last4;
  }
  return detailResponse;
};

export const getPaymentMethod = async ({
  customerId,
  paymentId,
}: {
  customerId: string;
  paymentId: string;
}): Promise<PaymentDetailResponse> => {
  let detailResponse: PaymentDetailResponse = {
    type: "",
    card: {
      brand: "",
      exp_month: 0,
      exp_year: 0,
      last4: "",
    },
  };

  if (paymentId == "") {
    const customer = await stripeApiClient.customers.retrieve(customerId);
    if (customer && !customer.deleted) {
      const paymentMethod = customer.invoice_settings.default_payment_method;
      if (typeof paymentMethod === "string") {
        paymentId = paymentMethod ?? "";
      } else if (paymentMethod != null) {
        return convertPaymentMethodToResponseObject({
          paymentMethod: paymentMethod,
        });
      }

      if (paymentId == "") {
        let customerSource = customer.default_source;
        if (typeof customerSource === "string") {
          customerSource = await stripeApiClient.customers.retrieveSource(
            customerId,
            customerSource
          );
        }

        if (customerSource && customerSource.object == "card") {
          detailResponse.type = customerSource.object;
          detailResponse.card.brand = customerSource.brand;
          detailResponse.card.exp_month = customerSource.exp_month;
          detailResponse.card.exp_year = customerSource.exp_year;
          detailResponse.card.last4 = customerSource.last4;
          return detailResponse;
        }
      }
    }
  }

  if (paymentId && paymentId != "") {
    const paymentMethod = await stripeApiClient.paymentMethods.retrieve(
      paymentId
    );
    if (paymentMethod) {
      return convertPaymentMethodToResponseObject({
        paymentMethod: paymentMethod,
      });
    }
  }

  return detailResponse;
};

export const getCustomerPortalLink = async (
  userEmail: string
): Promise<string> => {
  let customerId: string = "";
  let finalLink: string = "";
  try {
    const customers = await stripeApiClient.customers.list({
      email: userEmail,
      limit: 1,
    });
    if (customers.data.length > 0) {
      customerId = customers.data[0].id as string;
    }
  } catch (error) {
    console.error(error);
  }
  if (customerId != "") {
    const portalSession = await stripeApiClient.billingPortal.sessions.create({
      customer: customerId,
    });
    finalLink = portalSession.url;
  }
  return finalLink;
};

export const subscriptionHandler = async ({
  userId,
  customerId,
  query,
  body,
  headerData,
}: {
  userId: string;
  customerId: string;
  query: any;
  body: any;
  headerData?: any;
}) => {
  if (query.action === "redirectToCheckout") {
    return await redirectToCheckout({ userId, customerId, body });
  }

  if (query.action === "redirectToCustomerPortal") {
    return await redirectToCustomerPortal({ customerId, body });
  }

  if (query.action === "redirectToCustomerPortalSubscriptionCancel") {
    return await redirectToCustomerPortalSubscriptionCancel({
      customerId,
      body,
    });
  }

  if (query.action === "redirectToCustomerPortalSubscriptionUpdate") {
    return await redirectToCustomerPortalSubscriptionUpdate({
      customerId,
      body,
    });
  }

  return { error: "Action not found" };
};

async function redirectToCustomerPortal({
  customerId,
  body,
}: {
  customerId: string;
  body: any;
}) {
  return await stripeApiClient.billingPortal.sessions.create({
    customer: customerId,
    return_url: body.returnUrl,
  });
}

async function redirectToCustomerPortalSubscriptionCancel({
  customerId,
  body,
}: {
  customerId: string;
  body: any;
}) {
  return await stripeApiClient.billingPortal.sessions.create({
    customer: customerId,
    return_url: body.returnUrl,
    flow_data: {
      type: "subscription_cancel",
      subscription_cancel: {
        subscription: body.subscription,
      },
    },
  });
}

async function redirectToCustomerPortalSubscriptionUpdate({
  customerId,
  body,
}: {
  customerId: string;
  body: any;
}) {
  return await stripeApiClient.billingPortal.sessions.create({
    customer: customerId,
    return_url: body.returnUrl,
    flow_data: {
      type: "subscription_update",
      subscription_update: {
        subscription: body.subscription,
      },
    },
  });
}

export const resumeSubscription = async ({
  subscriptionId,
}: {
  subscriptionId: string;
}): Promise<boolean> => {
  if (subscriptionId != "") {
    const subscription = await stripeApiClient.subscriptions.resume(
      subscriptionId,
      { billing_cycle_anchor: "unchanged" }
    );
    if (subscription != null) {
      return true;
    }
  }
  return false;
};

async function redirectToCheckout({
  userId,
  customerId,
  body,
}: {
  userId: string;
  customerId: string;
  body: any;
}) {
  const configurations =
    await stripeApiClient.billingPortal.configurations.list({
      is_default: true,
      expand: ["data.features.subscription_update.products"],
    });

  // Make sure the price ID is in here somewhere
  let go = false;
  for (let product of configurations.data[0].features.subscription_update
    .products ?? []) {
    for (let price of product.prices) {
      if (price === body.price) {
        go = true;
        break;
      }
    }
  }

  if (go) {
    try {
      const sessionParams: any = {
        customer: customerId,
        success_url: body.successUrl,
        cancel_url: body.cancelUrl,
        line_items: [{ price: body.price, quantity: 1 }],
        mode: "subscription",
        client_reference_id: userId,
        tax_id_collection: {
          enabled: true,
        },
        customer_update: {
          name: "auto",
          address: "auto",
        },
      };

      if (body.discountId) {
        sessionParams["discounts"] = [
          {
            coupon: body.discountId,
          },
        ];
      } else {
        sessionParams["allow_promotion_codes"] = true;
      }

      const session = await stripeApiClient.checkout.sessions.create(
        sessionParams
      );
      return session;
    } catch (error) {
      console.error(error);
    }
  }
  return { error: "Error" };
}
