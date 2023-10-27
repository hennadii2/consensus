// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import { TrackEventData } from "helpers/services/mixpanel/events";
import { trackEvent } from "helpers/services/mixpanel/server";
import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<{}>
) {
  try {
    const { userId } = getAuth(req);
    const data = req.body;
    trackEvent(userId, data as TrackEventData);
    res.status(200).json({});
  } catch (error: any) {
    let status = 500;

    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }

    res.status(status);
  }
}
