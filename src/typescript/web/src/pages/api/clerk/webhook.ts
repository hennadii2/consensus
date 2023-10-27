import { addOrUpdateListMember } from "helpers/mailchimp";
import { identifyAuthMethodFromEmailAddresses } from "helpers/services/clerk";
import { MixpanelEvent } from "helpers/services/mixpanel/events";
import { trackSignUpEvent } from "helpers/services/mixpanel/server";
import { buffer } from "micro";
import { Webhook } from "svix";

export const config = {
  api: {
    bodyParser: false,
  },
};

const webhookSecret: string = process.env.CLERK_WEBHOOK_SECRET as string;

const handler = async (req: any, res: any) => {
  if (req.method === "POST") {
    const payload = (await buffer(req)).toString();
    const headers = req.headers;

    const wh = new Webhook(webhookSecret);
    let msg: any;
    try {
      msg = wh.verify(payload, headers);
    } catch (err) {
      res.status(400).end("Verify signature failed");
      return;
    }

    if (msg) {
      const evtType = msg.type as string;
      switch (evtType) {
        case "user.created":
          const userEmail = msg.data.email_addresses.find(
            (x: any) => x.id === msg.data.primary_email_address_id
          )?.email_address;
          const userFirstName = msg.data.first_name;
          const userLastName = msg.data.last_name;

          if (userEmail) {
            await addOrUpdateListMember({
              email: userEmail,
              firstName: userFirstName,
              lastName: userLastName,
            });
          }

          const authMethod = identifyAuthMethodFromEmailAddresses(
            msg.data.email_addresses
          );
          trackSignUpEvent(msg.data.id, {
            event: MixpanelEvent.SignUp,
            authMethod,
            createdAt: msg.data.created_at,
          });

          break;

        case "user_updated":
        case "user_deleted":
          break;
      }
      res.status(200).end();
    } else {
      res.status(400).end();
    }
  } else {
    res.setHeader("Allow", "POST");
    res.status(405).end("Method Not Allowed");
  }
};
export default handler;
