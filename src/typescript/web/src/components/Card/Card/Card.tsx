import classNames from "classnames";
import React, { ReactNode } from "react";

type CardProps = {
  className?: string;
  children: ReactNode;
  [rest: string]: any;
};

/**
 * @component Card
 * @description Container component for elements that has card styling
 * @example
 * return (
 *   <Card>This is a card</Card>
 * )
 */
const Card = ({ className = "", children, ...rest }: CardProps) => {
  return (
    <div
      data-testid="card"
      {...rest}
      className={classNames(
        "bg-white bg-opacity-70 rounded-3xl p-[26px] pb-[34px] sm:pb-[26px] shadow-card",
        className
      )}
    >
      {children}
    </div>
  );
};

export default Card;
