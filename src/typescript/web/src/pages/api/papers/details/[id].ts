// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import { getIp, getPaperDetails, PaperDetailsResponse } from "helpers/api";
import { MixpanelEvent } from "helpers/services/mixpanel/events";
import { trackEvent } from "helpers/services/mixpanel/server";
import { getPaperDetailsParams } from "helpers/testingQueryParams";
import type { NextApiRequest, NextApiResponse } from "next";

interface ErrorResponse {
  message: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<PaperDetailsResponse | ErrorResponse>
) {
  try {
    const { userId, getToken } = getAuth(req);
    const authToken = await getToken();
    const ipAddress = await getIp(req);

    const paperId = req.query.id as string;
    const headers = {
      authToken,
      ipAddress,
      headers: req.headers,
    };

    const queryParams = getPaperDetailsParams(req.query);
    const data = await getPaperDetails(paperId, headers, queryParams);

    trackEvent(userId, {
      event: MixpanelEvent.PaperView,
      paperId,
      paperTitle: data.title,
      publishYear: data.year,
      journalName: data.journal.title,
      firstAuthor: data.authors.length ? data.authors[0] : null,
      doi: data.doi,
    });

    res.status(200).json(data);
  } catch (error: any) {
    let status = 500;

    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }

    res.status(status).json({ message: error?.message });
  }
}
