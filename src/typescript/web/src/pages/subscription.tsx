import { useAuth } from "@clerk/nextjs";
import { withServerSideAuth } from "@clerk/nextjs/ssr";
import { useQuery } from "@tanstack/react-query";
import classNames from "classnames";
import Head from "components/Head";
import {
  SubscriptionBillingCard,
  SubscriptionCancelConfirmModal,
  SubscriptionCurrentPlanCard,
  SubscriptionUpgradeCard,
  SubscriptionUpgradeFeaturesCard,
  SubscriptionUsageCard,
  useSubscription,
} from "components/Subscription";
import SubscriptionResumeConfirmModal from "components/Subscription/SubscriptionResumeConfirmModal/SubscriptionResumeConfirmModal";
import {
  SALES_EMAIL,
  STRIPE_PRICE_METADATA_TYPE_LIFETIME,
} from "constants/config";
import path from "constants/path";
import { SubscriptionPlan } from "enums/subscription-plans";
import { getPaymentMethodDetailAPI } from "helpers/api";
import { subscriptionPageUrl } from "helpers/pageUrl";
import { findSubscriptionProduct, getUpgradePrice } from "helpers/products";
import { PaymentDetailResponse } from "helpers/stripe";
import {
  getActiveSubscription,
  getSubscriptionProducts,
  getSubscriptionUsageData,
  isSubscriptionPremium,
  ISubscriptionUsageData,
} from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import type { NextPage } from "next";
import { useRouter } from "next/router";
import { useCallback, useEffect, useState } from "react";
import {
  setProducts,
  setSubscription,
  setSubscriptionUsageData,
} from "store/slices/subscription";

type SubscriptionProps = {};

const Subscription: NextPage<SubscriptionProps> = ({}: SubscriptionProps) => {
  const [pageLabels] = useLabels("screens.subscription");
  const { isSignedIn, isLoaded } = useAuth();
  const router = useRouter();
  const dispatch = useAppDispatch();
  const subscription = useAppSelector(
    (state) => state.subscription.subscription
  );
  const subscriptionUsageData = useAppSelector(
    (state) => state.subscription.usageData
  );
  const products = useAppSelector((state) => state.subscription.products);
  const [openCancelConfirmModal, setOpenCancelConfirmmModal] =
    useState<boolean>(false);
  const [openResumeConfirmModal, setOpenResumeConfirmmModal] =
    useState<boolean>(false);
  const initialPaymentMethodDetail: any = null;
  const [paymentMethodDetail, setPaymentMethodDetail] = useState(
    initialPaymentMethodDetail
  );
  const [isFirstRunQuery, setIsFirstRunQuery] = useState<boolean>(true);
  const returnUrl = subscriptionPageUrl();
  const {
    redirectToCheckout,
    redirectToCustomerPortal,
    redirectToCustomerPortalSubscriptionCancel,
    redirectToCustomerPortalSubscriptionUpdate,
    redirectToCustomerPortalPaymentMethodManagement,
    redirectToCustomerPortalSubscriptionReactivate,
  } = useSubscription();

  const getSubscriptionQuery = useQuery(
    ["user-active-subscription"],
    async () => {
      const sortedProducts = await getSubscriptionProducts();
      dispatch(setProducts(sortedProducts));

      try {
        const activeSubscription = await getActiveSubscription({});
        dispatch(setSubscription(activeSubscription));
        if (activeSubscription?.user) {
          const paymentMethodDetailRet: PaymentDetailResponse =
            await getPaymentMethodDetailAPI(
              activeSubscription.user.default_payment_method ?? ""
            );
          setPaymentMethodDetail(paymentMethodDetailRet);
        }

        const data: ISubscriptionUsageData = await getSubscriptionUsageData(
          activeSubscription
        );
        dispatch(setSubscriptionUsageData(data));
      } catch (err) {
        console.error(err);
      }
      setIsFirstRunQuery(false);
      return true;
    }
  );

  const subscriptionProduct = findSubscriptionProduct(products, subscription);
  let upgradePlan: SubscriptionPlan = SubscriptionPlan.PREMIUM;
  let upgradePrice: any;

  if (subscription.user == null) {
    upgradePlan = SubscriptionPlan.PREMIUM;
    if (products) {
      upgradePrice = getUpgradePrice(products, upgradePlan);
    }
    if (subscription.org) {
      upgradePlan = SubscriptionPlan.ENTERPRISE;
    }
  } else {
    upgradePlan = SubscriptionPlan.ENTERPRISE;
  }

  const clickedUpgradePlan = useCallback(() => {
    if (upgradePlan == SubscriptionPlan.PREMIUM) {
      if (!isLoaded) {
        router?.push(path.INTERNAL_SERVER_ERROR);
        return;
      }

      if (!isSignedIn) {
        router.push(
          `${path.SIGN_UP}#/?redirect_url=${encodeURIComponent(
            `${subscriptionPageUrl("click")}`
          )}`
        );
        return;
      }

      if (subscription.user || !upgradePrice) {
        redirectToCustomerPortal!({ returnUrl: returnUrl });
      } else {
        redirectToCheckout!({ price: upgradePrice.id });
      }
    } else if (upgradePlan == SubscriptionPlan.ENTERPRISE) {
      window.location.href = "mailto:" + SALES_EMAIL;
    }
  }, [
    subscription,
    upgradePrice,
    redirectToCustomerPortal,
    redirectToCheckout,
    router,
    returnUrl,
    upgradePlan,
    isLoaded,
    isSignedIn,
  ]);

  useEffect(() => {
    (async () => {
      if (isLoaded && isSignedIn && router?.query.action) {
        if (
          getSubscriptionQuery.isLoading == false &&
          getSubscriptionQuery.fetchStatus == "idle"
        ) {
          await router.replace(subscriptionPageUrl());
          clickedUpgradePlan();
        }
      }
    })();
    return () => {};
  }, [isSignedIn, isLoaded, router, getSubscriptionQuery, clickedUpgradePlan]);

  useEffect(() => {
    (async () => {
      if (isLoaded && isSignedIn == false) {
        router.push(
          `${path.SIGN_UP}#/?redirect_url=${encodeURIComponent(
            `${subscriptionPageUrl()}`
          )}`
        );
      }
    })();
    return () => {};
  }, [isSignedIn, isLoaded, router]);

  const clickedManagePaymentMethod = async () => {
    if (subscription.user) {
      redirectToCustomerPortalPaymentMethodManagement!({
        subscriptionId: subscription.user.id,
        returnUrl: returnUrl,
      });
    }
  };

  const clickedCancelSubscription = useCallback(() => {
    if (subscription.user) {
      redirectToCustomerPortalSubscriptionCancel!({
        returnUrl: returnUrl,
        subscription: subscription.user.id,
      });
    }
  }, [returnUrl, redirectToCustomerPortalSubscriptionCancel, subscription]);

  const showCancelConfirmModal = useCallback(() => {
    if (subscription.user) {
      setOpenCancelConfirmmModal(true);
    }
  }, [subscription, setOpenCancelConfirmmModal]);

  const hideCancelConfirmModal = useCallback(() => {
    setOpenCancelConfirmmModal(false);
  }, [setOpenCancelConfirmmModal]);

  const clickedUpdateSubscription = useCallback(() => {
    if (subscription.user) {
      redirectToCustomerPortalSubscriptionUpdate!({
        returnUrl: returnUrl,
        subscription: subscription.user.id,
      });
    }
  }, [returnUrl, redirectToCustomerPortalSubscriptionUpdate, subscription]);

  const clickedReactivateSubscription = useCallback(() => {
    if (subscription.user) {
      redirectToCustomerPortalSubscriptionReactivate!({
        returnUrl: returnUrl,
        subscriptionId: subscription.user.id,
      });
    }
  }, [returnUrl, redirectToCustomerPortalSubscriptionReactivate, subscription]);

  const showResumeConfirmModal = useCallback(() => {
    if (subscription.user) {
      setOpenResumeConfirmmModal(true);
    }
  }, [subscription, setOpenResumeConfirmmModal]);

  const hideResumeConfirmModal = useCallback(() => {
    setOpenResumeConfirmmModal(false);
  }, [setOpenResumeConfirmmModal]);

  const isPageLoading =
    !products ||
    products.length == 0 ||
    (getSubscriptionQuery.isLoading && isFirstRunQuery);

  return (
    <>
      <Head
        title={pageLabels["title"]}
        description={pageLabels["description"]}
        type="website"
        url={subscriptionPageUrl()}
      />
      <div className="container pt-4 md:pt-16 md:pb-16">
        <h2 className="text-[#222F2B] max-w-[812px] text-center text-3xl sm:text-5xl font-bold mb-3 ml-[auto] mr-[auto] leading-tight">
          {pageLabels["page-title"]}
        </h2>
        <p className="text-black text-center text-base sm:text-lg mb-8 ml-[auto] mr-[auto]">
          {pageLabels["page-subtitle"]}
        </p>

        <div className="flex justify-center flex-wrap mt-5">
          <div className="w-full lg:w-[50%] border-b border-r-0 lg:border-b-0 lg:border-r border-[#DEE0E3]">
            <div
              className={`bg-white rounded-tr-3xl rounded-tl-3xl rounded-bl-none lg:rounded-tr-none lg:rounded-tl-3xl lg:rounded-bl-3xl shadow-card w-full h-full py-8 px-8`}
            >
              <SubscriptionUsageCard
                subscriptionUsageData={subscriptionUsageData}
                isLoading={isPageLoading}
                isPremium={isSubscriptionPremium(subscription)}
              />
            </div>
          </div>

          <div className="w-full lg:w-[50%]">
            <div
              className={`bg-white rounded-bl-3xl rounded-br-3xl rounded-tr-none lg:rounded-bl-none lg:rounded-tr-3xl lg:rounded-br-3xl shadow-card w-full h-full py-8 px-8`}
            >
              <SubscriptionUpgradeCard
                upgradePlan={upgradePlan}
                unit_amount={
                  upgradePrice
                    ? upgradePrice.recurring.interval == "year"
                      ? upgradePrice.unit_amount / 12.0
                      : upgradePrice.unit_amount
                    : undefined
                }
                interval={
                  upgradePrice ? upgradePrice.recurring.interval : undefined
                }
                isLoading={isPageLoading}
                onClick={clickedUpgradePlan}
              />
            </div>
          </div>
        </div>

        <div className="flex flex-wrap mt-5">
          <div className="w-full lg:w-[60%] pr-0 lg:pr-2">
            <div
              className={`bg-white rounded-3xl shadow-card w-full h-full py-8 px-8`}
            >
              <SubscriptionCurrentPlanCard
                plan_name={
                  subscription.org || subscription.user
                    ? SubscriptionPlan.PREMIUM
                    : SubscriptionPlan.FREE
                }
                interval={
                  subscription.user && subscription.user.plan.interval == "year"
                    ? "year"
                    : "month"
                }
                unit_amount={
                  subscription.user ? subscription.user.plan.amount_decimal : 0
                }
                onCancelClick={
                  subscription.user ? showCancelConfirmModal : undefined
                }
                onResumeClick={
                  subscription.user ? clickedReactivateSubscription : undefined
                }
                onUpgradeAnnualClick={
                  subscription.user ? clickedUpdateSubscription : undefined
                }
                isLifeTimePremium={Boolean(
                  subscriptionProduct &&
                    subscriptionProduct.price &&
                    subscriptionProduct.price.metadata.type ==
                      STRIPE_PRICE_METADATA_TYPE_LIFETIME
                )}
                subscription={subscription}
                isLoading={isPageLoading}
              />
            </div>
          </div>

          {(subscription.user || !subscription.org) && (
            <div className="w-full mt-5 lg:mt-0 lg:w-[40%] pl-0 lg:pl-2">
              <div
                className={classNames(
                  "rounded-3xl shadow-card w-full h-full py-8 px-8",
                  !subscription.user && !isPageLoading
                    ? "bg-[linear-gradient(76deg,_#0A6DC2_-84%,_#2BAE90_141%)]"
                    : "bg-white"
                )}
              >
                {!subscription.user && !subscription.org && (
                  <SubscriptionUpgradeFeaturesCard
                    plan_name={SubscriptionPlan.PREMIUM}
                    onUpgradeAnnualClick={clickedUpgradePlan}
                    isLoading={isPageLoading}
                  />
                )}

                {subscription.user && (
                  <SubscriptionBillingCard
                    userSubscription={subscription.user}
                    paymentMethodDetail={paymentMethodDetail}
                    onClick={clickedManagePaymentMethod}
                    isLoading={isPageLoading}
                  />
                )}
              </div>
            </div>
          )}
        </div>

        <SubscriptionCancelConfirmModal
          open={openCancelConfirmModal}
          onClose={hideCancelConfirmModal}
          onClickButton={clickedCancelSubscription}
        />

        <SubscriptionResumeConfirmModal
          open={openResumeConfirmModal}
          onClose={hideResumeConfirmModal}
          onClickButton={clickedUpdateSubscription}
        />
      </div>
    </>
  );
};

export const getServerSideProps = withServerSideAuth(
  async ({ query, req }) => {
    return {
      props: {},
    };
  },
  { loadUser: true }
);

export default Subscription;
