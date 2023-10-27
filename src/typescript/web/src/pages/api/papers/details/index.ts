// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import {
  getIp,
  getPapersList,
  GetPapersListOptions,
  PapersListResponse,
} from "helpers/api";
import type { NextApiRequest, NextApiResponse } from "next";

interface ErrorResponse {
  message: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<PapersListResponse | ErrorResponse>
) {
  try {
    const { getToken } = getAuth(req);
    const authToken = await getToken();
    const ipAddress = await getIp(req);

    const paperIds = (req.query.paper_ids as string).split(",");

    const includeAbstract = req.query.include_abstract === "true";
    const includeJournal = req.query.include_journal === "true";
    const enablePaperSearch = req.query.enable_paper_search === "true";

    const options: GetPapersListOptions = {
      includeAbstract,
      includeJournal,
      enablePaperSearch,
    };

    const headers = {
      authToken,
      ipAddress,
      headers: req.headers,
    };

    const data = await getPapersList(paperIds, options, headers);

    res.status(200).json(data);
  } catch (error: any) {
    let status = 500;
    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }
    res.status(status).json({ message: error?.message });
  }
}
