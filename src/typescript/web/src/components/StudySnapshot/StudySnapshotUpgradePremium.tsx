import { MAX_CREDIT_NUM } from "constants/config";
import { pricingPageUrl } from "helpers/pageUrl";
import useLabels from "hooks/useLabels";
import { useAppDispatch } from "hooks/useStore";
import Link from "next/link";
import React from "react";
import { setOpenUpgradeToPremiumPopup } from "store/slices/subscription";

interface StudySnapshotUpgradePremiumProps {
  isDetail?: boolean;
}

function StudySnapshotUpgradePremium({
  isDetail,
}: StudySnapshotUpgradePremiumProps) {
  const [pageLabels] = useLabels("study-snapshot");
  const dispatch = useAppDispatch();

  const onClickUpgradeToPremium = () => {
    dispatch(setOpenUpgradeToPremiumPopup(true));
  };

  return (
    <div
      data-testid="study-snapshot-upgrade-premium"
      className="flex flex-wrap justify-between items-start md:items-center"
    >
      <div className="inline-block rounded-[12px] p-[10px] md:p-[11px] bg-[#F1F4F6]">
        <img
          src={"/icons/premium.svg"}
          className="md:w-[32px] md:h-[32px] w-[24px] h-[24px]"
          alt="premium icon"
        />
      </div>

      <div className="flex-1 md:ml-[16px] ml-[12px]">
        <div className="text-base md:text-lg text-black">
          <span
            data-testid="study-snapshot-text1"
            dangerouslySetInnerHTML={{
              __html: pageLabels["unlock-with-premium"].replace(
                "{max-count}",
                MAX_CREDIT_NUM
              ),
            }}
          ></span>
        </div>

        <div className="text-base text-[#688092] mt-[6px]">
          <span>{pageLabels["unlock-with-premium-desc1"]}</span>
          <span className="ml-1 mr-1 text-[#0A6DC2] font-bold">
            <Link href={pricingPageUrl()} legacyBehavior>
              {pageLabels["unlock-with-premium-pricing"]}
            </Link>
          </span>
          <span>{pageLabels["unlock-with-premium-desc2"]}</span>
        </div>
      </div>
      {!isDetail ? (
        <button
          data-testid="study-snapshot-btn-upgrade-premium"
          onClick={onClickUpgradeToPremium}
          className="w-full md:w-auto md:mt-0 md:mb-0 mt-[16px] mb-[10px] bg-[#0A6DC2] text-sm text-white px-[20px] py-[7px] rounded-full cursor-pointer"
        >
          {pageLabels["upgrade-to-premium"]}
        </button>
      ) : null}
    </div>
  );
}

export default StudySnapshotUpgradePremium;
