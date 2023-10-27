// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import { deleteBookmarkItemAPI, getIp } from "helpers/api";
import type { NextApiRequest, NextApiResponse } from "next";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  try {
    const { userId, getToken } = getAuth(req);
    if (!userId) {
      res.status(401).json({ message: "Not logged in" });
      return;
    }

    const authToken = await getToken();
    const ipAddress = await getIp(req);

    switch (req.method) {
      case "DELETE":
        // Parse and validate the id
        const id = parseInt(req.query.id as string);
        if (isNaN(id)) {
          res.status(400).json({ message: "Invalid ID provided." });
          return;
        }

        const dataDelete = await deleteBookmarkItemAPI(id, {
          authToken,
          ipAddress,
          headers: req.headers,
        });
        res.status(200).json(dataDelete);
        break;

      default:
        res.status(405).json({ message: "Method not allowed" });
        break;
    }
  } catch (error: any) {
    let status = 500;

    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }

    res.status(status).json({ message: error.message });
  }
}
