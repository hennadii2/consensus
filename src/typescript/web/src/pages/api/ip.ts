import type { NextApiRequest, NextApiResponse } from "next";
import requestIp from "request-ip";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const ip = requestIp.getClientIp(req);

  res.status(200).json({ ip });
}
