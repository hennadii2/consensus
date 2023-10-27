import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import { getClerkPublicMetaData } from "helpers/clerk";
import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { userId } = getAuth(req);
  if (!userId) {
    res.status(401).send("Not logged in");
    return;
  }

  try {
    const publicMetaData = await getClerkPublicMetaData({
      clerkUserId: userId,
    });
    res.status(200).json(publicMetaData);
  } catch (error: any) {
    let status = 500;

    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }

    res.status(status).json({ message: error.message });
  }
}
