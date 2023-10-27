import Button from "components/Button";
import { pricingPageUrl } from "helpers/pageUrl";
import useLabels from "hooks/useLabels";
import { useAppDispatch } from "hooks/useStore";
import Link from "next/link";
import React from "react";
import { setOpenUpgradeToPremiumPopup } from "store/slices/subscription";

function QuestionSummaryFeatureLimited() {
  const [summaryLabels] = useLabels("question-summary");
  const dispatch = useAppDispatch();

  const onClickUpgradeToPremium = () => {
    dispatch(setOpenUpgradeToPremiumPopup(true));
  };

  return (
    <div className="mt-4">
      <div className="text-sm text-center flex flex-col gap-y-4 bg-[#F1F4F6] text-[#364B44] rounded-lg p-4">
        <p>
          <strong className="mr-1">
            {summaryLabels["feature-limit"]["title"]}
          </strong>
          {summaryLabels["feature-limit"]["desc"]}
        </p>
      </div>

      <div className="flex mt-4 flex-wrap lg:flex-nowrap">
        <div className="text-center lg:text-left lg:flex-1 text-sm w-full lg:w-auto">
          <span className="text-[#364B44]">
            {summaryLabels["want-unlimited"]}
          </span>
          <span className="ml-1 text-[#0A6DC2] font-bold">
            <Link href={pricingPageUrl()} legacyBehavior>
              {summaryLabels["view-pricing"]}
            </Link>
          </span>
        </div>

        <div className="flex items-center justify-center lg:justify-start text-sm w-full lg:w-auto mt-3 lg:mt-0">
          <img
            src={"/icons/premium.svg"}
            className="w-[20px] h-[20px] mr-2"
            alt="Premium"
          />
          <span className="text-[#0A6DC2] font-bold">
            <Button
              type="button"
              onClick={onClickUpgradeToPremium}
              className="font-bold"
            >
              {summaryLabels["upgrade-to-premium"]}
            </Button>
          </span>
        </div>
      </div>
    </div>
  );
}

export default QuestionSummaryFeatureLimited;
