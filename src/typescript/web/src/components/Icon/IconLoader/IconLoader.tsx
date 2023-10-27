import * as React from "react";

/**
 * @component IconLoader
 * @description loader for any component - button, div, ...
 * @example
 * return (
 *   <IconLoader />
 * )
 */
type IconLoaderProps = {
  color?: string;
};

const IconLoader = ({ color }: IconLoaderProps) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 100 100"
    xmlSpace="preserve"
    data-testid="icon-loader"
  >
    <circle fill={color ? color : "#00992B"} cx={6} cy={50} r={6}>
      <animateTransform
        attributeName="transform"
        dur="1s"
        type="translate"
        values="0 15 ; 0 -15; 0 15"
        repeatCount="indefinite"
        begin={0.1}
      />
    </circle>
    <circle fill={color ? color : "#00992B"} cx={30} cy={50} r={6}>
      <animateTransform
        attributeName="transform"
        dur="1s"
        type="translate"
        values="0 10 ; 0 -10; 0 10"
        repeatCount="indefinite"
        begin={0.2}
      />
    </circle>
    <circle fill={color ? color : "#00992B"} cx={54} cy={50} r={6}>
      <animateTransform
        attributeName="transform"
        dur="1s"
        type="translate"
        values="0 5 ; 0 -5; 0 5"
        repeatCount="indefinite"
        begin={0.3}
      />
    </circle>
  </svg>
);

export default IconLoader;
