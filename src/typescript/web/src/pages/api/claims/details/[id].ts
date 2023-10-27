// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import { ClaimDetailsResponse, getClaimDetails, getIp } from "helpers/api";
import { MixpanelEvent } from "helpers/services/mixpanel/events";
import { trackEvent } from "helpers/services/mixpanel/server";
import { getClaimDetailsParams } from "helpers/testingQueryParams";
import type { NextApiRequest, NextApiResponse } from "next";

interface ErrorResponse {
  message: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ClaimDetailsResponse | ErrorResponse>
) {
  try {
    const { userId, getToken } = getAuth(req);
    const authToken = await getToken();
    const ipAddress = await getIp(req);

    const claimId = req.query.id as string;
    const headers = {
      authToken,
      ipAddress,
      headers: req.headers,
    };

    const queryParams = getClaimDetailsParams(req.query);
    const data = await getClaimDetails(claimId, headers, queryParams);

    trackEvent(userId, {
      event: MixpanelEvent.ClaimView,
      claimId,
      claimText: data.claim.text,
      paperTitle: data.paper.title,
      publishYear: data.paper.year,
      journalName: data.paper.journal.title,
      firstAuthor: data.paper.authors.length ? data.paper.authors[0] : null,
      doi: data.paper.doi,
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
