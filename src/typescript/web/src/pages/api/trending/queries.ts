// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import { getAuth } from "@clerk/nextjs/server";
import { getIp, getTrending } from "helpers/api";
import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<any>
) {
  try {
    const { getToken } = getAuth(req);
    const authToken = await getToken();
    const ipAddress = await getIp(req);

    const data = await getTrending({
      authToken,
      ipAddress,
      headers: req.headers,
    });
    res.status(200).json(data);
  } catch (error: any) {
    res.status(500).json({ message: error?.message });
  }
}
