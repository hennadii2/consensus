import { useQuery } from "@tanstack/react-query";
import Modal from "components/Modal";
import PricingSwitch, {
  PricingSwitchFlag,
} from "components/Pricing/PricingSwitch/PricingSwitch";
import { useSubscription } from "components/Subscription";
import {
  STUDENT_DISCOUNT_1_YEAR,
  STUDENT_DISCOUNT_1_YEAR_PERCENT,
  STUDENT_DISCOUNT_2_YEAR,
  STUDENT_DISCOUNT_2_YEAR_PERCENT,
  STUDENT_DISCOUNT_3_YEAR,
  STUDENT_DISCOUNT_3_YEAR_PERCENT,
  STUDENT_DISCOUNT_4_YEAR,
  STUDENT_DISCOUNT_4_YEAR_PERCENT,
} from "constants/config";
import { roundDownSignificantDigits } from "helpers/format";
import { getMonthAnnualPrices } from "helpers/products";
import {
  getFeatureCopyList,
  getPremiumProduct,
  getSubscriptionProducts,
} from "helpers/subscription";
import useLabels from "hooks/useLabels";
import { useAppDispatch, useAppSelector } from "hooks/useStore";
import React, { useState } from "react";
import { setProducts } from "store/slices/subscription";

/**
 * @component StudentPremiumModal
 * @description Component for student premium modal
 * @example
 * return (
 *   <StudentPremiumModal />
 * )
 */
type StudentPremiumModalProps = {
  open?: boolean;
  year?: string;
  onClose: () => void;
};

function StudentPremiumModal({
  open,
  year,
  onClose,
}: StudentPremiumModalProps) {
  const dispatch = useAppDispatch();
  const [pageLabels] = useLabels("student-discount.premium-modal");
  const [activeFlag, setActiveFlag] = useState(PricingSwitchFlag.ANNUALLY);
  const products = useAppSelector((state) => state.subscription.products);
  let features_list: string[] = [];
  const currencyFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "usd",
    minimumFractionDigits: 3,
    maximumFractionDigits: 10,
    minimumSignificantDigits: 3,
    maximumSignificantDigits: 10,
  });
  const { redirectToCheckout } = useSubscription();
  let discountId = STUDENT_DISCOUNT_1_YEAR;
  let discountPercent = STUDENT_DISCOUNT_1_YEAR_PERCENT;

  if (year && year.length >= 4) {
    const thisYear = new Date().getFullYear();
    const diffYears = Number(year.substring(0, 4)) - thisYear;

    if (diffYears == 1) {
      discountId = STUDENT_DISCOUNT_1_YEAR;
      discountPercent = STUDENT_DISCOUNT_1_YEAR_PERCENT;
    } else if (diffYears == 2) {
      discountId = STUDENT_DISCOUNT_2_YEAR;
      discountPercent = STUDENT_DISCOUNT_2_YEAR_PERCENT;
    } else if (diffYears == 3) {
      discountId = STUDENT_DISCOUNT_3_YEAR;
      discountPercent = STUDENT_DISCOUNT_3_YEAR_PERCENT;
    } else if (diffYears == 4) {
      discountId = STUDENT_DISCOUNT_4_YEAR;
      discountPercent = STUDENT_DISCOUNT_4_YEAR_PERCENT;
    }
  }

  useQuery(
    ["subscription-products-query"],
    async () => {
      const sortedProducts = await getSubscriptionProducts();
      dispatch(setProducts(sortedProducts));
    },
    {
      enabled: open,
    }
  );
  const premiumProduct = getPremiumProduct(products);
  if (premiumProduct) {
    features_list = getFeatureCopyList(premiumProduct);
  }
  let { monthPrice, annualPrice } = getMonthAnnualPrices(products);

  const handleClickGetStarted = () => {
    onClose();
    if (activeFlag == PricingSwitchFlag.MONTHLY && monthPrice) {
      redirectToCheckout({ price: monthPrice.id, discountId: discountId });
    }

    if (activeFlag == PricingSwitchFlag.ANNUALLY && annualPrice) {
      redirectToCheckout({ price: annualPrice.id, discountId: discountId });
    }
  };

  return (
    <>
      <Modal
        open={open}
        onClose={onClose}
        size="md"
        padding={false}
        overflowVisible={true}
        mobileFit={true}
        additionalClass={"mt-[0px] max-w-[565px]"}
      >
        <div
          className="p-12 bg-[url('/images/bg-card.webp')] bg-no-repeat text-[#364B44] leading-tight rounded-lg"
          data-testid="student-premium-modal"
        >
          <img
            src={"/icons/x-blue.svg"}
            className="w-[24px] h-[24px] cursor-pointer absolute top-[20px] right-[20px] md:top-[32px] md:right-[32px]"
            onClick={onClose}
            alt="X"
          />

          <div className="text-center">
            <span className="inline-block p-5 bg-white rounded-full">
              <img
                src={"/icons/premium-student.svg"}
                className="w-[64px] h-[64px]"
                alt="Premium Student"
              />
            </span>
          </div>

          <div className="text-[22px] text-center font-bold mt-[20px]">
            <span className="mr-1">{pageLabels["title1"]}</span>
            <span className="mr-1 text-[#009FF5]">{pageLabels["title2"]}</span>
            <span>{pageLabels["title3"]}</span>
          </div>

          <div className="mt-6 text-center">
            <PricingSwitch
              onChange={(currentFlag) => {
                setActiveFlag(currentFlag);
              }}
              initialFlag={PricingSwitchFlag.ANNUALLY}
            />
          </div>

          <div className="mt-2">
            {activeFlag == PricingSwitchFlag.MONTHLY && monthPrice && (
              <div className="text-center">
                <span className="text-4xl font-bold">
                  {currencyFormatter.format(
                    roundDownSignificantDigits(
                      (monthPrice.unit_amount * (100 - discountPercent)) /
                        100 /
                        100,
                      3
                    )
                  )}
                </span>
                <span className="text-lg text-[#688092]">
                  {" "}
                  /{pageLabels["per-month"]}
                </span>
              </div>
            )}

            {activeFlag == PricingSwitchFlag.ANNUALLY && annualPrice && (
              <>
                <div className="text-center">
                  <span className="text-4xl font-bold">
                    {currencyFormatter.format(
                      roundDownSignificantDigits(
                        (annualPrice.unit_amount * (100 - discountPercent)) /
                          100 /
                          100,
                        3
                      )
                    )}
                  </span>
                  <span className="text-lg text-[#688092]">
                    {" "}
                    /{pageLabels["per-year"]}
                  </span>
                </div>

                <div className="text-center text-[12px] text-[#688092]">
                  <span className="mr-1">{pageLabels["equivalent-to"]}</span>
                  <span className="">
                    {currencyFormatter.format(
                      roundDownSignificantDigits(
                        (annualPrice.unit_amount * (100 - discountPercent)) /
                          100 /
                          12 /
                          100,
                        3
                      )
                    )}
                  </span>
                  <span className=""> /{pageLabels["per-month"]}</span>
                </div>
              </>
            )}
          </div>

          <div className="mt-3">
            {activeFlag == PricingSwitchFlag.MONTHLY && monthPrice && (
              <div className="text-center text-[14px] text-[#C6211F] line-through">
                <span className="">
                  {currencyFormatter.format(
                    roundDownSignificantDigits(monthPrice.unit_amount / 100, 3)
                  )}
                </span>
                <span className=""> /{pageLabels["per-month"]}</span>
              </div>
            )}

            {activeFlag == PricingSwitchFlag.ANNUALLY && annualPrice && (
              <div className="text-center text-[14px] text-[#C6211F] line-through">
                <span className="">
                  {currencyFormatter.format(
                    roundDownSignificantDigits(annualPrice.unit_amount / 100, 3)
                  )}
                </span>
                <span className=""> /{pageLabels["per-year"]}</span>
              </div>
            )}
          </div>

          <div className="mt-6 text-center">
            <div className="flex-wrap inline-block">
              {features_list.map((feature: any) => (
                <div
                  key={`feature-${feature}`}
                  className="flex items-center mt-2 feture-list-item align-center gap-x-2"
                >
                  <img
                    src={"/icons/check-mark.svg"}
                    className="w-[20px] h-[20px] text-sm"
                    alt="check-mark"
                  />
                  <span className="flex-1 text-sm leading-tight text-left sm:text-base">
                    {feature}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-8">
            <button
              onClick={handleClickGetStarted}
              className="flex w-full justify-center bg-[#0A6DC2] text-white py-3 rounded-full items-center cursor-pointer"
            >
              {pageLabels["button-discount"]}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}

export default StudentPremiumModal;
