import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import { findStripeCustomerId, resumeSubscription } from "helpers/stripe";

const handler = async (req: any, res: any) => {
  try {
    const { userId } = getAuth(req);
    if (!userId) {
      res.status(401).json({ message: "Not logged in" });
      return;
    }

    const customerId = await findStripeCustomerId({
      clerkUserId: userId,
      createIfNotExist: false,
    });

    if (!customerId) {
      res.status(401).json({ message: "Not found stripe customer id" });
      return;
    }

    const subscriptionId = req.query.id as string;
    const ret = await resumeSubscription({
      subscriptionId,
    });
    res.status(200).send(ret);
  } catch (error: any) {
    let status = 500;

    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }

    res.status(status).json({ message: error.message });
  }
};
export default handler;
