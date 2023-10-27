// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import { getIp, getSubscriptionProductsAPI } from "helpers/api";
import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  try {
    const { getToken } = getAuth(req);

    const authToken = await getToken();
    const ipAddress = await getIp(req);

    const productId = req.query.product_id as string;
    const headers = {
      authToken,
      ipAddress,
      headers: req.headers,
    };
    const data = await getSubscriptionProductsAPI(productId, headers);

    res.status(200).json(data);
  } catch (error: any) {
    let status = 500;

    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }

    res.status(status).json({ message: error.message });
  }
}
