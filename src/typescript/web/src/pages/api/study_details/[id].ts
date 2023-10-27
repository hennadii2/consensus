// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import {
  getIp,
  getStudyDetailsResponse,
  StudyDetailsResponse,
} from "helpers/api";
import { getStudyDetailsEndpointParams } from "helpers/testingQueryParams";
import type { NextApiRequest, NextApiResponse } from "next";

interface ErrorResponse {
  message: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<StudyDetailsResponse | ErrorResponse>
) {
  try {
    const { getToken } = getAuth(req);
    const authToken = await getToken();
    const ipAddress = await getIp(req);

    const paperId = req.query.id as string;
    const params = getStudyDetailsEndpointParams(req.query);
    const headers = {
      authToken,
      ipAddress,
      headers: req.headers,
    };
    const data = await getStudyDetailsResponse(paperId, params, headers);
    res.status(200).json(data);
  } catch (error: any) {
    let status = 500;

    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }

    // Return 500 to force route to 500 UI error page
    if (status === 504) {
      status = 500;
    }

    res.status(status).json({ message: error.message });
  }
}
