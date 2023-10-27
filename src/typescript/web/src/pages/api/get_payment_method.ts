import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import {
  findStripeCustomerId,
  getPaymentMethod,
  PaymentDetailResponse,
} from "helpers/stripe";
import type { NextApiRequest, NextApiResponse } from "next";

interface ErrorResponse {
  message: string;
}

const handler = async (
  req: NextApiRequest,
  res: NextApiResponse<PaymentDetailResponse | ErrorResponse>
) => {
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

    const data = await getPaymentMethod({
      customerId: customerId,
      paymentId: req.query.id as string,
    });
    res.status(200).json(data);
  } catch (error: any) {
    let status = 500;

    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }

    res.status(status).json({ message: error?.message });
  }
};
export default handler;
