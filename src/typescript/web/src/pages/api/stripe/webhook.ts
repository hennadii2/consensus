import { clerkClient } from "@clerk/nextjs/server";
import {
  addCustomerSubscriptionAPI,
  deleteCustomerSubscriptionAPI,
} from "helpers/api";
import { Client } from "intercom-client";
import { buffer } from "micro";
import Stripe from "stripe";

export const config = {
  api: {
    bodyParser: false,
  },
};

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY as string, {
  apiVersion: "2022-11-15",
});

const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

const getClerkUserByEmail = async (email: string) => {
  const emailAddress = [email];
  const clerkUsers = await clerkClient.users.getUserList({ emailAddress });

  if (clerkUsers && clerkUsers.length == 1) {
    return clerkUsers[0];
  }

  return null;
};

const addStripeCustomerIdToClerkMetadata = async (
  clerkUserId: string,
  stripeCustomerId: string
): Promise<void> => {
  const clerkUser = await clerkClient.users.getUser(clerkUserId);
  if (clerkUser) {
    let publicMetadata = clerkUser.publicMetadata;
    publicMetadata.stripeCustomerId = stripeCustomerId;
    await clerkClient.users.updateUser(clerkUser.id, {
      publicMetadata: publicMetadata,
    });
  }
};

const addClerkUserIdToStripeMetadata = async (
  clerkUserId: string,
  stripeCustomerId: string
): Promise<void> => {
  await stripe.customers.update(stripeCustomerId, {
    metadata: {
      clerkUserId: clerkUserId,
    },
  });
};

const removeStripeCustomerIdFromClerkMetadata = async (
  clerkUserEmail: string
): Promise<void> => {
  const clerkUser = await getClerkUserByEmail(clerkUserEmail);
  if (clerkUser) {
    let publicMetadata = clerkUser.publicMetadata;
    publicMetadata.stripeCustomerId = null;
    await clerkClient.users.updateUser(clerkUser.id, {
      publicMetadata: publicMetadata,
    });
  }
};

const addStripeSubscriptionToUsersDb = async (
  stripeCustomerId: string,
  req: any
): Promise<void> => {
  const subscriptions = await stripe.subscriptions.list({
    customer: stripeCustomerId,
    status: "active",
    limit: 5,
  });

  if (subscriptions.data.length == 0) {
    // No subscription found, delete customer
    await deleteCustomerSubscriptionAPI(stripeCustomerId, {
      headers: req.headers,
    });
    return;
  }

  for (let i = 0; i < subscriptions.data.length; i++) {
    const subscriptionData: Stripe.Subscription = subscriptions.data[i];
    if (subscriptionData.items.data.length > 0) {
      await addCustomerSubscriptionAPI(
        stripeCustomerId,
        JSON.stringify(subscriptionData),
        {
          headers: req.headers,
        }
      );
      break;
    }
  }
};

const sendIntercomPurchaseEvent = async (
  stripeCustomerId: string,
  clerkUserId: string,
  req: any
): Promise<void> => {
  const client = new Client({
    tokenAuth: { token: process.env.INTERCOM_ACCESS_TOKEN as string },
  });
  const subscriptions = await stripe.subscriptions.list({
    customer: stripeCustomerId,
    status: "active",
    limit: 5,
  });

  if (subscriptions.data.length == 0) {
    // No subscription found, delete customer
    await deleteCustomerSubscriptionAPI(stripeCustomerId, {
      headers: req.headers,
    });
    return;
  }

  for (let i = 0; i < subscriptions.data.length; i++) {
    const subscriptionData: Stripe.Subscription = subscriptions.data[i];
    if (subscriptionData.items.data.length > 0) {
      for (let j = 0; j < subscriptionData.items.data.length; i++) {
        const subscriptionItem: Stripe.SubscriptionItem =
          subscriptionData.items.data[j];
        let plan = subscriptionItem.plan.metadata?.type || "premium";
        plan = plan.charAt(0).toUpperCase() + plan.slice(1);
        let billingPeriod = "Monthly";
        if (subscriptionItem.plan.interval === "day") billingPeriod = "Daily";
        if (subscriptionItem.plan.interval === "week") billingPeriod = "Weekly";
        if (subscriptionItem.plan.interval === "month")
          billingPeriod = "Monthly";
        if (subscriptionItem.plan.interval === "year")
          billingPeriod = "Annually";
        await client.events.create({
          eventName: "Purchase",
          createdAt: subscriptionData.created,
          userId: clerkUserId,
          metadata: {
            plan,
            billing_period: billingPeriod,
          },
        });
        break;
      }
      break;
    }
  }
};

const handler = async (req: any, res: any) => {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    res.status(405).end("Method Not Allowed");
    return;
  }

  const buf = await buffer(req);
  const sig = req.headers["stripe-signature"];

  let event;
  try {
    event = stripe.webhooks.constructEvent(buf, sig, webhookSecret!);
  } catch (err) {
    res.status(400).send(`Webhook Error: ${err}`);
    return;
  }

  const data: any = event.data.object;
  switch (event.type) {
    case "customer.subscription.created":
    case "customer.subscription.deleted":
    case "customer.subscription.paused":
    case "customer.subscription.pending_update_applied":
    case "customer.subscription.pending_update_expired":
    case "customer.subscription.resumed":
    case "customer.subscription.trial_will_end":
    case "customer.subscription.updated": {
      try {
        const stripeCustomerId = data.customer;
        await addStripeSubscriptionToUsersDb(stripeCustomerId, req);
      } catch (error) {
        res.status(500).end(error);
        return;
      }
      break;
    }
    case "customer.created":
    case "customer.updated":
      break;

    case "customer.deleted": {
      try {
        await removeStripeCustomerIdFromClerkMetadata(data.email);
        await deleteCustomerSubscriptionAPI(data.id, {
          headers: req.headers,
        });
      } catch (error) {
        res.status(500).end(error);
        return;
      }
      break;
    }

    case "checkout.session.completed": {
      try {
        const stripeCustomerId = data.customer;
        const clerkUserId = data.client_reference_id;
        if (!clerkUserId) {
          console.error(
            "Failed to resolve clerk to stripe: missing client_reference_id"
          );
          break;
        }
        await addStripeCustomerIdToClerkMetadata(clerkUserId, stripeCustomerId);
        await addClerkUserIdToStripeMetadata(clerkUserId, stripeCustomerId);
        await sendIntercomPurchaseEvent(stripeCustomerId, clerkUserId, req);
      } catch (error) {
        res.status(500).end(error);
        return;
      }
      break;
    }

    default:
      break;
  }
  res.status(200).end();
};

export default handler;
