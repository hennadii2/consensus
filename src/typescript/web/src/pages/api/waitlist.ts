import type { NextApiRequest, NextApiResponse } from "next";
const mailchimp = require("@mailchimp/mailchimp_marketing");

mailchimp.setConfig({
  apiKey: process.env.MAILCHIMP_API_KEY,
  server: process.env.MAILCHIMP_SERVER_PREFIX,
});

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  try {
    const email = req.body.email;
    const timestamp_signup = new Date().toISOString().slice(0, 19) + "Z";

    const response = await mailchimp.lists.addListMember(
      process.env.MAILCHIMP_LIST_ID,
      {
        email_address: email,
        status: "subscribed",
        timestamp_signup,
      }
    );

    res.status(200).json(response);
  } catch (error: any) {
    res.status(500).json(error.response?.body);
  }
}
