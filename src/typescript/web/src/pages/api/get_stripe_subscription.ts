// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import { getCustomerSubscriptionAPI, getIp } from "helpers/api";
import { getUserOrganizationName } from "helpers/clerk";
import { findStripeCustomerId } from "helpers/stripe";
import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  try {
    const { userId, getToken } = getAuth(req);
    if (!userId) {
      res.status(200).json({ message: "Not logged in" });
      return;
    }

    const customerId = await findStripeCustomerId({
      clerkUserId: userId,
      createIfNotExist: false,
    });

    if (!customerId) {
      res.status(200).json({});
      return;
    }

    const authToken = await getToken();
    const ipAddress = await getIp(req);

    const data = await getCustomerSubscriptionAPI(customerId, {
      authToken,
      ipAddress,
      headers: req.headers,
    });

    // TODO(meganvw): Creation of organization subscription would be better
    // done on the backend to return a full subscription object that the
    // frontend does not need to construct. Should be refactored.
    const org = await getUserOrganizationName({
      clerkUserId: data.clerk_user_id,
    });
    data.org_name = org;

    res.status(200).json(data);
  } catch (error: any) {
    let status = 500;

    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }

    res.status(status).json({ message: error.message });
  }
}
