import { MAILCHIMP_TAG, SUPPORT_EMAIL } from "constants/config";
import crypto from "crypto";

const mailchimp = require("@mailchimp/mailchimp_transactional")(
  process.env.MAILCHIMP_TRANSACTION_API_KEY as string
);

const mailchimpMarketing = require("@mailchimp/mailchimp_marketing");
mailchimpMarketing.setConfig({
  apiKey: process.env.MAILCHIMP_API_KEY,
  server: process.env.MAILCHIMP_SERVER_PREFIX,
});

export interface IEmailRequest {
  email: string;
  subject: string;
  body: string;
}

export default async function sendEmail(
  inputData: IEmailRequest
): Promise<boolean> {
  const message = {
    from_email: SUPPORT_EMAIL,
    subject: inputData.subject,
    html: inputData.body,
    to: [
      {
        email: inputData.email,
        type: "to",
      },
    ],
  };

  const response = await mailchimp.messages.send({
    message,
  });
  if (response && Array.isArray(response) && response.length > 0) {
    if (response[0]["status"] == "sent") {
      return true;
    }
  }
  return false;
}

export async function addOrUpdateListMember({
  email,
  firstName,
  lastName,
}: {
  email: string;
  firstName: string;
  lastName: string;
}): Promise<boolean> {
  const timestamp_signup = new Date().toISOString().slice(0, 19) + "Z";
  const subscriberHash = crypto
    .createHash("md5")
    .update(email.toLowerCase())
    .digest("hex");

  let isEmailExist: boolean = false;
  try {
    const response = await mailchimpMarketing.lists.getListMember(
      process.env.MAILCHIMP_LIST_ID,
      subscriberHash
    );
    isEmailExist = true;
  } catch (error) {
    console.log(error);
  }

  if (isEmailExist) {
    try {
      const response = await mailchimpMarketing.lists.setListMember(
        process.env.MAILCHIMP_LIST_ID,
        subscriberHash,
        {
          email_address: email,
          status_if_new: "subscribed",
          merge_fields: {
            FNAME: firstName,
            LNAME: lastName,
          },
          timestamp_signup,
          tags: [MAILCHIMP_TAG],
        }
      );
      return true;
    } catch (error) {
      console.log(error);
    }
  } else {
    try {
      const response = await mailchimpMarketing.lists.addListMember(
        process.env.MAILCHIMP_LIST_ID,
        {
          email_address: email,
          status: "subscribed",
          merge_fields: {
            FNAME: firstName,
            LNAME: lastName,
          },
          timestamp_signup,
          tags: [MAILCHIMP_TAG],
        }
      );
      return true;
    } catch (error) {
      console.log(error);
    }
  }
  return false;
}
