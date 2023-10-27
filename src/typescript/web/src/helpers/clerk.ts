import { clerkClient } from "@clerk/nextjs/server";
import {
  ALLOWED_ORG_DOMAINS_AND_FULL_ORG_NAME,
  CLERK_META_KEY_CREATED_DATE,
  CLERK_META_KEY_CREDIT_USE_NUM,
  CLERK_META_KEY_USED_STUDY_PAPER_IDS,
  CLERK_META_KEY_USED_SYNTHESIZED_QUERIES,
  MAX_CREDIT_LIMIT_DAYS,
} from "constants/config";
import { emailHasAllowedDomain, emailHasStudentDomain } from "./email";

export interface IClerkPublicMetaData {
  stripeCustomerId: string;
  credit_use_num: number;
  created_date: string;
  used_synthesized_queries: string[];
  used_study_paper_ids: string[];
}

export const getUserCreatedDate = async ({
  clerkUserId,
}: {
  clerkUserId: string;
}) => {
  let user = await clerkClient.users.getUser(clerkUserId);
  let userCreatedDate = new Date().toISOString();
  if (user.publicMetadata.userCreatedDate) {
    userCreatedDate = user.publicMetadata.userCreatedDate as string;
  }
  return userCreatedDate;
};

export const getUserOrganizationName = async ({
  clerkUserId,
}: {
  clerkUserId: string;
}): Promise<string | null> => {
  const clerkUser = await clerkClient.users.getUser(clerkUserId);
  for (const emailAddress of clerkUser.emailAddresses) {
    const allowedDomainOrNull = emailHasAllowedDomain(
      emailAddress.emailAddress,
      ALLOWED_ORG_DOMAINS_AND_FULL_ORG_NAME
    );
    if (allowedDomainOrNull) {
      return allowedDomainOrNull;
    }
  }
  return null;
};

export async function resetPublicMetaDataIfNeed(user: any): Promise<any> {
  let daysDiff = MAX_CREDIT_LIMIT_DAYS;
  if (user.publicMetadata[CLERK_META_KEY_CREATED_DATE]) {
    const userCreatedDate = new Date(
      user.publicMetadata[CLERK_META_KEY_CREATED_DATE] as string
    );
    const currentDate = new Date();
    const msInDay = 24 * 60 * 60 * 1000;
    daysDiff = Math.round(
      Math.abs(Number(currentDate) - Number(userCreatedDate)) / msInDay
    );
  }

  if (daysDiff >= MAX_CREDIT_LIMIT_DAYS) {
    const data = user.publicMetadata;
    data[CLERK_META_KEY_CREATED_DATE] = new Date().toISOString();
    data[CLERK_META_KEY_CREDIT_USE_NUM] = 0;
    data[CLERK_META_KEY_USED_SYNTHESIZED_QUERIES] = [];
    data[CLERK_META_KEY_USED_STUDY_PAPER_IDS] = [];

    const updatedUser = await clerkClient.users.updateUser(user.id, {
      publicMetadata: data,
    });
    return updatedUser.publicMetadata;
  }
  return user.publicMetadata;
}

export const getClerkPublicMetaData = async ({
  clerkUserId,
}: {
  clerkUserId: string;
}): Promise<any> => {
  const clerkUser = await clerkClient.users.getUser(clerkUserId);
  const updatedMetaData = await resetPublicMetaDataIfNeed(clerkUser);
  return updatedMetaData;
};

export const updateClerkPublicMetaData = async ({
  clerkUserId,
  inputData,
}: {
  clerkUserId: string;
  inputData: IClerkPublicMetaData;
}): Promise<any> => {
  let user = await clerkClient.users.getUser(clerkUserId);
  const data = user.publicMetadata;
  data[CLERK_META_KEY_CREDIT_USE_NUM] = inputData.credit_use_num;
  data[CLERK_META_KEY_USED_SYNTHESIZED_QUERIES] =
    inputData.used_synthesized_queries;
  data[CLERK_META_KEY_USED_STUDY_PAPER_IDS] = inputData.used_study_paper_ids;
  const updatedUser = await clerkClient.users.updateUser(clerkUserId, {
    publicMetadata: data,
  });
  return updatedUser.publicMetadata;
};

export const hasStudentEmailDomain = async ({
  clerkUserId,
}: {
  clerkUserId: string;
}): Promise<boolean> => {
  const clerkUser = await clerkClient.users.getUser(clerkUserId);
  for (const emailAddress of clerkUser.emailAddresses) {
    const isStudentEmailAddress = emailHasStudentDomain(
      emailAddress.emailAddress
    );
    if (isStudentEmailAddress) {
      return true;
    }
  }
  return false;
};
