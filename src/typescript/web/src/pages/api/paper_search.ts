// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import { getIp, getPaperSearch, PaperSearchResponse } from "helpers/api";
import getSearchTestingQueryParams from "helpers/search";
import type { NextApiRequest, NextApiResponse } from "next";

interface ErrorResponse {
  message: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<PaperSearchResponse | ErrorResponse>
) {
  try {
    const { getToken } = getAuth(req);
    const authToken = await getToken();
    const ipAddress = await getIp(req);

    const query = req.query.query as string;
    const page = Number(req.query.page || 0);
    const params = getSearchTestingQueryParams(req.query);
    const headers = {
      authToken,
      ipAddress,
      headers: req.headers,
    };
    const data = await getPaperSearch(query, page, params, headers);

    res.status(200).json(data);
  } catch (error: any) {
    let status = 500;

    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }

    res.status(status).json({ message: error?.message });
  }
}
