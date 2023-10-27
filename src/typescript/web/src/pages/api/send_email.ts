import axios from "axios";
import sendEmail from "helpers/mailchimp";
import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  try {
    const inputData = req.body.data;
    const data = await sendEmail(inputData);
    res.status(200).json(data);
  } catch (error: any) {
    let status = 500;

    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }

    res.status(status).json({ message: error.message });
  }
}
