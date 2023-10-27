// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import { getIp, getYesNoResults, YesNoResponse } from "helpers/api";
import { getYesNoEndpointParams } from "helpers/testingQueryParams";
import type { NextApiRequest, NextApiResponse } from "next";

interface ErrorResponse {
  message: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<YesNoResponse | ErrorResponse>
) {
  try {
    const { getToken } = getAuth(req);

    const authToken = await getToken();
    const ipAddress = await getIp(req);

    const searchId = req.query.search_id as string;
    const params = getYesNoEndpointParams(req.query);
    const headers = {
      authToken,
      ipAddress,
      headers: req.headers,
    };
    const data = await getYesNoResults(searchId, params, headers);

    res.status(200).json(data);
  } catch (error: any) {
    let status = 500;

    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }

    res.status(status).json({ message: error?.message });
  }
}
