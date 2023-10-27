import { STUDENT_EMAIL_DOMAINS } from "constants/config";

export const emailHasAllowedDomain = (
  emailAddress: string,
  allowedDomains: { [key: string]: string }
): string | null => {
  const emailDomain = emailAddress.split("@").pop();
  if (emailDomain) {
    for (const allowedDomain in allowedDomains) {
      if (emailDomain.endsWith(allowedDomain)) {
        return allowedDomains[allowedDomain];
      }
    }
  }
  return null;
};

export const emailHasStudentDomain = (emailAddress: string): boolean => {
  const emailDomain: string | undefined = emailAddress.split("@").pop();
  if (emailDomain) {
    const emailDomainArray: string[] = emailDomain.split(".");
    let isIncluded: boolean = false;
    STUDENT_EMAIL_DOMAINS.forEach((email_domain: string) => {
      if (emailDomainArray.includes(email_domain)) {
        isIncluded = true;
      }
    });
    return isIncluded;
  }
  return false;
};
