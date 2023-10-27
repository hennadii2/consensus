import { withServerSideAuth } from "@clerk/nextjs/ssr";
import Head from "components/Head";
import { SUPPORT_EMAIL } from "constants/config";
import { getCustomerPortalLinkAPI, sendEmailAPI } from "helpers/api";
import { IEmailRequest } from "helpers/mailchimp";
import useLabels from "hooks/useLabels";
import type { NextPage } from "next";
import { useCallback, useEffect, useState } from "react";

type UpdateEmailProps = {
  email?: string;
};

/**
 * @page Send Email Page
 * @description page for sending email with customer portal link
 */
const UpdateEmail: NextPage<UpdateEmailProps> = ({
  email,
}: UpdateEmailProps) => {
  const [pageLabels] = useLabels("screens.update-email");
  const [isSentEmail, setIsSentEmail] = useState<boolean | undefined>(
    undefined
  );
  const [calledSendEmailCallBack, setCalledSendEmailCallBack] = useState(false);

  const sendEmailCallBack = useCallback(async () => {
    if (email) {
      const portalLink = await getCustomerPortalLinkAPI(email);
      const emailBody = pageLabels["email-body"]
        .replaceAll("{email}", SUPPORT_EMAIL)
        .replace("{link}", portalLink);

      const request: IEmailRequest = {
        email: email,
        subject: pageLabels["email-subject"],
        body: emailBody,
      };
      const ret: boolean = await sendEmailAPI(request);
      setIsSentEmail(ret);
    }
  }, [email, pageLabels]);

  useEffect(() => {
    if (calledSendEmailCallBack == false) {
      setCalledSendEmailCallBack(true);
      sendEmailCallBack();
    }
  }, [sendEmailCallBack, calledSendEmailCallBack]);

  return (
    <>
      <Head
        title={pageLabels["title"]}
        description={pageLabels["description"]}
      />
      <div
        data-testid="update-email"
        className="container max-w-6xl m-auto mt-20 mb-20 text-center"
      >
        {isSentEmail == true && (
          <p
            dangerouslySetInnerHTML={{
              __html: pageLabels["success"].replaceAll(
                "{email}",
                SUPPORT_EMAIL
              ),
            }}
          />
        )}

        {isSentEmail == false && <p>{pageLabels["fail"]}</p>}
      </div>
    </>
  );
};

export const getServerSideProps = withServerSideAuth(async ({ query, req }) => {
  return {
    props: {
      email: query.email ? (query.email as string) : null,
    },
  };
});

export default UpdateEmail;
