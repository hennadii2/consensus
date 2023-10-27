import React, { ReactNode } from "react";

type Props = {
  children: ReactNode;
  onClick?: () => void;
  dataTestId?: string;
  className?: string;
  disabled?: boolean;
};

/**
 * @component ClaimButton
 * @description designed for claim button
 * @example
 * return (
 *   <ClaimButton onClick={fn}>Learn more</ClaimButton>
 * )
 */
const ClaimButton = ({
  children,
  onClick,
  dataTestId,
  className,
  disabled,
}: Props) => {
  return (
    <button
      onClick={onClick}
      data-testid={dataTestId}
      className={`text-base bg-blue-300 text-blue-600 flex items-center justify-center h-[44px] md:w-[auto] gap-x-3 px-2 md:px-[26px] rounded-full hover:shadow-[0_2px_4px_0_rgba(189,201,219,0.32)] ${className}`}
      disabled={disabled}
    >
      <img
        data-testid="upload-icon"
        alt="share"
        src="/icons/share.svg"
        className="w-5 h-5"
      />
      {children}
    </button>
  );
};

export default ClaimButton;
