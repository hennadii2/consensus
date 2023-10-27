import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import { getIp } from "helpers/api";
import { findStripeCustomerId, subscriptionHandler } from "helpers/stripe";
import type { NextApiRequest, NextApiResponse } from "next";

const handler = async (req: NextApiRequest, res: NextApiResponse) => {
  try {
    const { userId, getToken } = getAuth(req);
    if (!userId) {
      res.status(401).send({ message: "Not logged in" });
      return;
    }
    const customerId = await findStripeCustomerId({
      clerkUserId: userId,
      createIfNotExist: true,
    });

    if (!customerId) {
      res.status(401).json({ message: "Not found stripe customer id" });
      return;
    }

    const authToken = await getToken();
    const ipAddress = await getIp(req);

    res.json(
      await subscriptionHandler({
        userId,
        customerId,
        query: req.query,
        body: req.body,
        headerData: {
          authToken,
          ipAddress,
          headers: req.headers,
        },
      })
    );
  } catch (error: any) {
    let status = 500;

    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }

    res.status(status).json({ message: error.message });
  }
};

export default handler;
