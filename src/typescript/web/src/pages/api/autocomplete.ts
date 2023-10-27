// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import {
  AutocompleteResponse,
  getAutocompleteQuerySuggestions,
  getIp,
} from "helpers/api";
import { getAutocompleteEndpointParams } from "helpers/testingQueryParams";
import type { NextApiRequest, NextApiResponse } from "next";

interface ErrorResponse {
  message: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<AutocompleteResponse | ErrorResponse>
) {
  try {
    const { getToken } = getAuth(req);

    const authToken = await getToken();
    const ipAddress = await getIp(req);

    const params = getAutocompleteEndpointParams(req.query);

    const data = await getAutocompleteQuerySuggestions(
      req.query.query as string,
      params,
      {
        authToken,
        ipAddress,
        headers: req.headers,
      }
    );
    res.status(200).json(data);
  } catch (error: any) {
    let status = 500;

    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }

    res.status(status).json({ message: error?.message });
  }
}
