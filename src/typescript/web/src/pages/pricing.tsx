import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import Head from "components/Head";
import DiscountMessage from "components/Pricing/DiscountMessage/DiscountMessage";
import PricingCard from "components/Pricing/PricingCard";
import PricingSwitch, {
  PricingSwitchFlag,
} from "components/Pricing/PricingSwitch";
import ExistingEmailInstructionModal from "components/Pricing/StudentDiscount/ExistingEmailInstructionModal";
import GraduationYearModal from "components/Pricing/StudentDiscount/GraduationYearModal";
import MergeAccountModal from "components/Pricing/StudentDiscount/MergeAccountModal";
import NoEduEmailModal from "components/Pricing/StudentDiscount/NoEduEmailModal";
import StudentPremiumModal from "components/Pricing/StudentDiscount/StudentPremiumModal/StudentPremiumModal";
import { useSubscription } from "components/Subscription";
import {
  META_PRICING_IMAGE,
  STRIPE_PRICE_METADATA_TYPE_PREMIUM,
} from "constants/config";
import path from "constants/path";
import { SubscriptionPlan } from "enums/subscription-plans";
import { hasEduEmailDomain } from "helpers/api";
import { pricingPageUrl, searchPageUrl } from "helpers/pageUrl";
import {
  getActiveSubscription,
  getSubscriptionProducts,
} from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import { useRouter } from "next/router";
import { useCallback, useEffect, useState } from "react";
import { setProducts } from "store/slices/subscription";

const initialSubscription: any = null;

export default function SubscriptionManagePage() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const [pricingLabels] = useLabels("screens.pricing");
  const [activeFlag, setActiveFlag] = useState(PricingSwitchFlag.ANNUALLY);
  const products = useAppSelector((state) => state.subscription.products);
  const [subscription, setSubscription] = useState(initialSubscription);
  const { isSignedIn, isLoaded } = useAuth();
  const { redirectToCheckout, redirectToCustomerPortal } = useSubscription();
  const [isFirstRunQuery, setIsFirstRunQuery] = useState<boolean>(true);

  const getSubscriptionQuery = useQuery(
    ["get-customer-subscription", router.pathname],
    async () => {
      const activeSubscription = await getActiveSubscription({});
      setSubscription(activeSubscription);

      const sortedProducts = await getSubscriptionProducts();
      dispatch(setProducts(sortedProducts));

      setIsFirstRunQuery(false);
    }
  );

  const handleClickTrySearchForFree = () => {
    if (!isLoaded) {
      router?.push(path.INTERNAL_SERVER_ERROR);
      return;
    }

    if (!isSignedIn) {
      router.push(
        `${path.SIGN_UP}#/?redirect_url=${encodeURIComponent(
          `${searchPageUrl()}`
        )}`
      );
      return;
    }
  };

  const handleClickUpgrade = useCallback(
    async (price_id?: string) => {
      if (!isLoaded) {
        router?.push(path.INTERNAL_SERVER_ERROR);
        return;
      }

      if (!isSignedIn) {
        router.push(
          `${path.SIGN_UP}#/?redirect_url=${encodeURIComponent(
            `${pricingPageUrl(price_id)}`
          )}`
        );
        return;
      }

      if (subscription?.user) {
        redirectToCustomerPortal({ returnUrl: pricingPageUrl() });
      } else if (price_id) {
        redirectToCheckout({
          price: price_id,
          successUrl: searchPageUrl(),
          cancelUrl: pricingPageUrl(),
        });
      }
    },
    [
      router,
      isSignedIn,
      isLoaded,
      subscription,
      redirectToCustomerPortal,
      redirectToCheckout,
    ]
  );

  useEffect(() => {
    (async () => {
      if (isLoaded && isSignedIn && router?.query.price_id) {
        if (
          getSubscriptionQuery.isLoading == false &&
          getSubscriptionQuery.fetchStatus == "idle"
        ) {
          await router.replace(pricingPageUrl());
          handleClickUpgrade(router.query.price_id as string);
        }
      }
    })();
    return () => {};
  }, [isSignedIn, isLoaded, router, getSubscriptionQuery, handleClickUpgrade]);

  const [openMergeAccountModal, setOpenMergeAccountModal] = useState(false);
  const handleOpenMergeAccountModal = useCallback(async () => {
    setOpenMergeAccountModal(true);
  }, [setOpenMergeAccountModal]);
  const handleCloseMergeAccountModal = useCallback(async () => {
    setOpenMergeAccountModal(false);
  }, [setOpenMergeAccountModal]);

  const [
    openExistingEmailInstructionModal,
    setOpenExistingEmailInstructionModal,
  ] = useState(false);
  const handleOpenExistingEmailInstructionModal = useCallback(async () => {
    setOpenExistingEmailInstructionModal(true);
  }, [setOpenExistingEmailInstructionModal]);
  const handleCloseExistingEmailInstructionModal = useCallback(async () => {
    setOpenExistingEmailInstructionModal(false);
  }, [setOpenExistingEmailInstructionModal]);

  const [openNoEduEmailModal, setOpenNoEduEmailModal] = useState(false);
  const handleCloseNoEduEmailModal = useCallback(async () => {
    setOpenNoEduEmailModal(false);
  }, [setOpenNoEduEmailModal]);

  const [openAskGraduationYearModal, setOpenAskGraduationYearModal] =
    useState(false);
  const handleOpenGraduationYearModal = useCallback(async () => {
    setOpenAskGraduationYearModal(true);
  }, [setOpenAskGraduationYearModal]);
  const handleCloseGraduationYearModal = useCallback(async () => {
    setOpenAskGraduationYearModal(false);
  }, [setOpenAskGraduationYearModal]);

  const handleVerifyEduAccount = useCallback(async () => {
    if (!isLoaded) {
      router?.push(path.INTERNAL_SERVER_ERROR);
      return;
    }

    if (!isSignedIn) {
      router.push(
        `${path.SIGN_IN}#/?redirect_url=${encodeURIComponent(
          `${pricingPageUrl()}`
        )}`
      );
      return;
    }

    try {
      const hasEdu: boolean = await hasEduEmailDomain();
      if (hasEdu) {
        setOpenAskGraduationYearModal(true);
      } else {
        setOpenNoEduEmailModal(true);
      }
    } catch (error) {}
  }, [
    router,
    isSignedIn,
    isLoaded,
    setOpenNoEduEmailModal,
    setOpenAskGraduationYearModal,
  ]);

  const [openStudentPremiumModal, setOpenStudentPremiumModal] = useState(false);
  const [selectedGraduationYear, setSelectedGraduationYear] = useState("");
  const handleOpenPremiumModal = useCallback(async () => {
    setOpenStudentPremiumModal(true);
  }, [setOpenStudentPremiumModal]);
  const handleCloseStudentPremiumModal = useCallback(async () => {
    setOpenStudentPremiumModal(false);
  }, [setOpenStudentPremiumModal]);

  const handleSelectGraduationYear = useCallback(
    async (value: string) => {
      setSelectedGraduationYear(value);
      setOpenStudentPremiumModal(true);
    },
    [setSelectedGraduationYear]
  );

  const isPageLoading =
    !products ||
    products.length == 0 ||
    !isLoaded ||
    (getSubscriptionQuery.isLoading && isFirstRunQuery);

  return (
    <>
      <Head
        title={pricingLabels["title"]}
        description={pricingLabels["description"]}
        type="website"
        url={pricingPageUrl()}
        image={META_PRICING_IMAGE}
      />

      <div className="container max-w-7xl m-auto grid grid-cols-1 pt-4 md:pt-16 md:pb-16">
        <h2 className="text-[#222F2B] max-w-[812px] text-center text-3xl md:text-5xl font-bold mb-3 ml-[auto] mr-[auto] leading-tight">
          <span className="hidden md:block">{pricingLabels["page-title"]}</span>
          <span className="block md:hidden">
            {pricingLabels["page-title-mobile"]}
          </span>
        </h2>
        <p className="text-black max-w-[735px] text-center text-base hidden md:block md:text-lg mb-8 ml-[auto] mr-[auto]">
          {pricingLabels["page-subtitle"]}
        </p>

        <PricingSwitch
          onChange={(currentFlag) => {
            setActiveFlag(currentFlag);
          }}
          initialFlag={PricingSwitchFlag.ANNUALLY}
        />

        <div className="flex justify-center flex-wrap gap-x-3 gap-y-6 mt-5">
          <div key="product-free" className="w-full md:w-[32%]">
            <PricingCard
              onClick={(price?: any) => {
                handleClickTrySearchForFree();
              }}
              title={SubscriptionPlan.FREE}
              subscription={subscription}
              className="bg-[#FFFFFF] text-[#222F2B]"
              isLoading={isPageLoading}
            />
          </div>
          {products.map(
            ({
              product_id,
              product_data,
            }: {
              product_id: string;
              product_data: any;
            }) =>
              product_data.prices.map((price: any) =>
                (activeFlag == PricingSwitchFlag.MONTHLY &&
                  price.metadata.type == STRIPE_PRICE_METADATA_TYPE_PREMIUM &&
                  price.recurring != null &&
                  price.recurring.interval == "month") ||
                (activeFlag == PricingSwitchFlag.ANNUALLY &&
                  price.metadata.type == STRIPE_PRICE_METADATA_TYPE_PREMIUM &&
                  price.recurring != null &&
                  price.recurring.interval == "year") ? (
                  <div
                    key={`${product_id}_${price.id}`}
                    className="w-full md:w-[32%]"
                  >
                    <PricingCard
                      onClick={(price?: any) => {
                        if (price?.unit_amount == 0) {
                          handleClickUpgrade();
                        } else {
                          handleClickUpgrade(price?.id);
                        }
                      }}
                      title={product_data.name}
                      product={product_data}
                      price={price}
                      subscription={subscription}
                      className="bg-[#FFFFFF] text-[#222F2B]"
                      isLoading={isPageLoading}
                    />
                  </div>
                ) : (
                  ""
                )
              )
          )}

          <div key="product-enterprise" className="w-full md:w-[32%]">
            <PricingCard
              onClick={(price?: any) => {}}
              title={SubscriptionPlan.ENTERPRISE}
              className="bg-[#FFFFFF] text-[#222F2B]"
              isLoading={isPageLoading}
            />
          </div>

          <div key="discount-message" className="w-full md:w-[500px]">
            <DiscountMessage
              onClickVerifyAccount={handleVerifyEduAccount}
              onClickShowInstructionToMergeAccount={handleOpenMergeAccountModal}
              onClickShowExistingEmailInstruction={
                handleOpenExistingEmailInstructionModal
              }
            />
          </div>
        </div>
      </div>

      <MergeAccountModal
        open={openMergeAccountModal}
        onClose={handleCloseMergeAccountModal}
      />
      <ExistingEmailInstructionModal
        open={openExistingEmailInstructionModal}
        onClose={handleCloseExistingEmailInstructionModal}
      />
      <NoEduEmailModal
        open={openNoEduEmailModal}
        onClose={handleCloseNoEduEmailModal}
      />
      <GraduationYearModal
        open={openAskGraduationYearModal}
        onClose={handleCloseGraduationYearModal}
        onSelect={handleSelectGraduationYear}
      />
      <StudentPremiumModal
        open={openStudentPremiumModal}
        year={selectedGraduationYear}
        onClose={handleCloseStudentPremiumModal}
      />
    </>
  );
}
