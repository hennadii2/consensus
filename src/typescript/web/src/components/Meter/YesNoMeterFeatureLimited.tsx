import Button from "components/Button";
import { pricingPageUrl } from "helpers/pageUrl";
import useLabels from "hooks/useLabels";
import { useAppDispatch } from "hooks/useStore";
import Link from "next/link";
import React from "react";
import { setOpenUpgradeToPremiumPopup } from "store/slices/subscription";

function YesNoMeterFeatureLimited() {
  const [meterLabels] = useLabels("meter");
  const dispatch = useAppDispatch();

  const onClickUpgradeToPremium = () => {
    dispatch(setOpenUpgradeToPremiumPopup(true));
  };

  return (
    <div className="mt-4">
      <div className="flex bg-[#F1F4F6] text-center text-[#364B44] rounded-lg p-4 text-sm">
        <p>
          <strong className="mr-1">
            {meterLabels["feature-limit"]["bold-text"]}
          </strong>
          <span>{meterLabels["feature-limit"]["explanation"]}</span>
        </p>
      </div>

      <div className="flex mt-4 flex-wrap lg:flex-nowrap">
        <div className="text-center lg:text-left lg:flex-1 text-sm w-full lg:w-auto">
          <span className="text-[#364B44]">
            {meterLabels["want-unlimited"]}
          </span>
          <span className="ml-1 text-[#0A6DC2] font-bold">
            <Link href={pricingPageUrl()} legacyBehavior>
              {meterLabels["view-pricing"]}
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
              {meterLabels["upgrade-to-premium"]}
            </Button>
          </span>
        </div>
      </div>
    </div>
  );
}

export default YesNoMeterFeatureLimited;
