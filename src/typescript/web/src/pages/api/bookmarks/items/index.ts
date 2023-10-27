// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import { getAuth } from "@clerk/nextjs/server";
import axios from "axios";
import {
  createBookmarkItemsAPI,
  getBookmarkItemsAPI,
  getIp,
} from "helpers/api";
import { IBookmarkCreateItemData } from "helpers/bookmark";
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
      case "GET":
        const dataGet = await getBookmarkItemsAPI({
          authToken,
          ipAddress,
          headers: req.headers,
        });
        res.status(200).json(dataGet);
        break;

      case "POST":
        const dataPost = await createBookmarkItemsAPI(
          req.body.items as IBookmarkCreateItemData[],
          {
            authToken,
            ipAddress,
            headers: req.headers,
          }
        );
        res.status(200).json(dataPost);
        break;

      default:
        res.status(405).json({ message: "Method not allowed" });
    }
  } catch (error: any) {
    let status = 500;

    if (axios.isAxiosError(error) && error.response?.status) {
      status = error.response?.status;
    }

    res.status(status).json({ message: error.message });
  }
}
