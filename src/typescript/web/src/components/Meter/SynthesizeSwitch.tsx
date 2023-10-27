import Switch from "components/Switch/Switch";
import Tooltip from "components/Tooltip";
import SynthesizeToggleTooltip from "components/Tooltip/SynthesizeToggleTooltip/SynthesizeToggleTooltip";
import useLabels from "hooks/useLabels";
import { useAppDispatch } from "hooks/useStore";
import React, { useState } from "react";
import { setOpenUpgradeToPremiumPopup } from "store/slices/subscription";

interface SynthesizeSwitchProps {
  canSynthesize?: boolean;
  isLoading?: boolean;
  isSynthesizeOn?: boolean;
  isEmpty?: boolean;
  handleOnChange: (value: boolean) => void;
}

function SynthesizeSwitch({
  canSynthesize,
  isLoading,
  isSynthesizeOn,
  isEmpty,
  handleOnChange,
}: SynthesizeSwitchProps) {
  const dispatch = useAppDispatch();
  const [questionSummaryLabels] = useLabels("question-summary");
  const [tooltipInstance, setTooltipInstance] = useState<any>(null);
  const [isTooltipVisible, setIsTooltipVisible] = useState<boolean>(false);
  const handleClickUpgradePremium = async () => {
    dispatch(setOpenUpgradeToPremiumPopup(true));
    tooltipInstance?.hide();
  };

  return (
    <div data-testid="meter" className="flex items-center gap-x-2">
      <div className="flex items-center">
        {canSynthesize || isLoading || isEmpty ? (
          <Switch
            disabled={!canSynthesize || isLoading || isEmpty}
            active={isSynthesizeOn}
            onChange={(state) => {
              handleOnChange(state);
            }}
          />
        ) : null}
      </div>
      <Tooltip
        theme={!canSynthesize ? "primary" : undefined}
        disabled={isLoading || isEmpty}
        interactive={canSynthesize}
        maxWidth={canSynthesize ? 340 : null}
        onShown={(instance: any) => {
          if (canSynthesize) {
            setIsTooltipVisible(true);
            setTooltipInstance(instance);
          }
        }}
        onHidden={(instance: any) => {
          if (canSynthesize) {
            setIsTooltipVisible(false);
            setTooltipInstance(instance);
          }
        }}
        tooltipContent={
          canSynthesize ? (
            <SynthesizeToggleTooltip
              onClickUpgradeToPremium={handleClickUpgradePremium}
            />
          ) : (
            <div>
              <p className="text-lg font-bold">
                {questionSummaryLabels["try-question-title"]}
              </p>
              <p className="text-base mt-1">
                {questionSummaryLabels["try-question-desc"]}
              </p>
            </div>
          )
        }
      >
        <div className="flex items-center gap-x-2">
          {!(canSynthesize || isLoading || isEmpty) ? (
            <Switch
              disabled={!canSynthesize || isLoading || isEmpty}
              active={isSynthesizeOn}
              onChange={(state) => {
                handleOnChange(state);
              }}
            />
          ) : null}
          <img
            className="min-w-[24px] max-w-[24px] h-6 w-6 ml-1"
            alt="Sparkler"
            src="/icons/sparkler.svg"
          />
          <span
            className={
              isLoading || isEmpty ? "text-gray-400" : "text-[#364B44]"
            }
          >
            {questionSummaryLabels["synthesize"]}
          </span>
          {isLoading || isEmpty ? null : (
            <img
              className="min-w-[20px] max-w-[20px] h-5"
              alt="Info"
              src="/icons/info.svg"
            />
          )}
        </div>
      </Tooltip>
    </div>
  );
}

export default SynthesizeSwitch;
