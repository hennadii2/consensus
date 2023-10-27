import { MAX_CREDIT_NUM } from "constants/config";
import crypto from "crypto";
import {
  getClerkPublicMetaDataAPI,
  getCustomerSubscriptionAPI,
  getSubscriptionProductsAPI,
  updateClerkPublicMetaDataAPI,
} from "./api";
import { IClerkPublicMetaData } from "./clerk";
import { sortProducts } from "./products";

export interface ISubscriptionUsageData {
  stripeCustomerId: string;
  creditUsageNum: number;
  userCreatedDate: string;
  synthesizedQueries: string[];
  studyPaperIds: string[];
  isSet: boolean;
}

export interface SubscriptionUsageSummary {
  creditLeft: number;
  refreshDate: string;
}

export interface UserSubscription {
  cancel_at_period_end?: boolean;
  cancel_at: number;
  current_period_end: number;
  default_payment_method?: string;
  id: string;
  plan: {
    amount_decimal: number;
    amount: number;
    id: string;
    interval: string;
    product: string;
  };
  status: string;
}

export interface OrganizationSubscription {
  orgName: string;
}

export interface ISubscriptionData {
  user: UserSubscription | null;
  org: OrganizationSubscription | null;
}

export const getActiveSubscription = async ({
  customerId,
  headerData,
}: {
  customerId?: string;
  headerData?: any;
}): Promise<ISubscriptionData> => {
  let subscription = null;

  let subscriptionRes = await getCustomerSubscriptionAPI(
    customerId,
    headerData
  );

  let organizationSubscription: OrganizationSubscription | null = null;
  if (subscriptionRes && subscriptionRes.org_name) {
    organizationSubscription = { orgName: subscriptionRes.org_name };
  }

  try {
    subscription = subscriptionRes.user_subscription || null;
    subscription = subscription ? JSON.parse(subscription!) : null;
    if (subscription.status != "active") {
      subscription = null;
    } else if (subscription.cancel_at_period_end) {
      if (Date.now() > subscription.cancel_at * 1000) {
        subscription = null;
      }
    }
  } catch (error) {
    subscription = null;
  }

  return { user: subscription, org: organizationSubscription };
};

export const getSubscriptionProducts = async () => {
  let sortedProducts = null;
  const subscriptionProducts = await getSubscriptionProductsAPI("");
  if (subscriptionProducts) {
    sortedProducts = sortProducts(
      subscriptionProducts["subscription_products"]
    );
  }
  return sortedProducts;
};

export function getFeatureCopyList(product?: any): string[] {
  if (product && product.metadata["feature_copy_list"]) {
    return product.metadata["feature_copy_list"].split("|");
  }
  return [];
}

export function isSubscriptionCanceledNotExpired(
  userSubscription: UserSubscription | null
): boolean {
  if (
    userSubscription &&
    userSubscription.status == "active" &&
    userSubscription.cancel_at_period_end
  ) {
    return Date.now() <= userSubscription.cancel_at * 1000 ? true : false;
  }
  return false;
}

export function getPremiumProduct(products: any) {
  for (let i = 0; i < products.length; i++) {
    const productData = products[i].product_data;
    if (productData.metadata.tier == "premium") {
      return productData;
    }
  }
  return null;
}

export async function applySubscriptionUsageDataToClerkPublicMetaData(
  data: ISubscriptionUsageData
): Promise<ISubscriptionUsageData> {
  const publicMetaData: IClerkPublicMetaData = {
    created_date: data.userCreatedDate,
    stripeCustomerId: data.stripeCustomerId,
    credit_use_num: data.creditUsageNum,
    used_synthesized_queries: data.synthesizedQueries,
    used_study_paper_ids: data.studyPaperIds,
  };
  const updatedPublicMetaData = await updateClerkPublicMetaDataAPI(
    publicMetaData
  );
  const updatedSubscriptionUsageData: ISubscriptionUsageData = {
    creditUsageNum: updatedPublicMetaData.credit_use_num,
    userCreatedDate: updatedPublicMetaData.created_date,
    synthesizedQueries: updatedPublicMetaData.used_synthesized_queries,
    studyPaperIds: updatedPublicMetaData.used_study_paper_ids,
    stripeCustomerId: updatedPublicMetaData.stripeCustomerId,
    isSet: true,
  };

  return updatedSubscriptionUsageData;
}

export async function getSubscriptionUsageData(
  subscription: ISubscriptionData
): Promise<ISubscriptionUsageData> {
  const publicMetaData: IClerkPublicMetaData =
    await getClerkPublicMetaDataAPI();
  let data: ISubscriptionUsageData = {
    creditUsageNum: publicMetaData.credit_use_num
      ? publicMetaData.credit_use_num
      : 0,
    userCreatedDate: publicMetaData.created_date
      ? publicMetaData.created_date
      : new Date().toISOString(),
    synthesizedQueries: publicMetaData.used_synthesized_queries
      ? publicMetaData.used_synthesized_queries
      : [],
    studyPaperIds: publicMetaData.used_study_paper_ids
      ? publicMetaData.used_study_paper_ids
      : [],
    stripeCustomerId: publicMetaData.stripeCustomerId,
    isSet: true,
  };
  return data;
}

export function getReversedSubscriptionUsageData(
  subscriptionUsageData: ISubscriptionUsageData
): SubscriptionUsageSummary {
  let data: SubscriptionUsageSummary = {
    creditLeft: 0,
    refreshDate: new Date().toISOString(),
  };

  data.creditLeft = MAX_CREDIT_NUM - subscriptionUsageData.creditUsageNum!;
  if (data.creditLeft < 0) data.creditLeft = 0;
  let refreshDate = new Date(subscriptionUsageData.userCreatedDate!);
  refreshDate.setDate(refreshDate.getDate() + 30);

  const dateOptions: Intl.DateTimeFormatOptions = {
    month: "long",
    day: "2-digit",
    year: "numeric",
  };
  data.refreshDate = refreshDate.toLocaleDateString("en-US", dateOptions);
  return data;
}

export function hashQuery(query: string): string {
  const queryHash = crypto.createHash("md5").update(query).digest("hex");
  return queryHash;
}

export function isSubscriptionPremium(
  subscription: ISubscriptionData
): boolean {
  const isPremium = Boolean(subscription.user || subscription.org);
  return isPremium;
}
