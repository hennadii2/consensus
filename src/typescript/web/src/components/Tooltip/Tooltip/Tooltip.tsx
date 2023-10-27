import Tippy from "@tippyjs/react";
import classNames from "classnames";
import { useAppSelector } from "hooks/useStore";
import React, {
  cloneElement,
  JSXElementConstructor,
  ReactElement,
  useEffect,
  useState,
} from "react";
import "tippy.js/animations/scale-subtle.css";
import "tippy.js/dist/tippy.css";
import "tippy.js/themes/light.css";

type Props = {
  children: ReactElement<any, string | JSXElementConstructor<any>> | undefined;
  tooltipContent: ReactElement<any, string | JSXElementConstructor<any>>;
  theme?: string;
  placement?:
    | "top-end"
    | "top-start"
    | "bottom-end"
    | "bottom-start"
    | "left"
    | "right";
  [rest: string]: any;
  delay?: number;
  disabled?: boolean;
  widthFull?: boolean;
};

/**
 * @component Tooltip
 * @description Wrapper component for tooltips
 * @example
 * return (
 *   <Tooltip content={<ReactComponent />}>Learn more</Tooltip>
 * )
 */
const Tooltip = ({
  tooltipContent,
  children,
  placement = "top-end",
  theme = "light",
  disabled,
  widthFull,
  ...rest
}: Props) => {
  const [body, setBody] = useState<HTMLElement | null>(null);
  const [open, setOpen] = useState<boolean>(false);
  const [clickOutsideActive, setClickOutsideActive] = useState<boolean>(false);
  const isMobile = useAppSelector((state) => state.setting.isMobile);

  useEffect(() => {
    setBody(document?.body);
  }, []);

  const handleClickOutside = () => {};

  const handleShow = () => {
    if (isMobile) {
      setOpen(true);
      setTimeout(() => {
        setClickOutsideActive(true);
      }, 100);
    }
  };

  const handleHide = () => {
    setOpen(false);
    setClickOutsideActive(false);
  };

  if (!body) return null;

  if (disabled) {
    return <>{children}</>;
  }

  return (
    <>
      <Tippy
        content={cloneElement(tooltipContent)}
        animation="scale-subtle"
        theme={theme}
        placement={placement}
        offset={[5, 5]}
        maxWidth={280}
        appendTo={body}
        onShow={handleShow}
        trigger={isMobile ? "click" : "mouseenter"}
        onHide={handleHide}
        zIndex={99999999999}
        className="rounded-xl"
        {...rest}
      >
        <span
          className={classNames("flex", widthFull ? "w-full" : "w-fit")}
          data-testid="tooltip"
        >
          {children}
          {open && (
            <div
              id="tippy-backdrop"
              onClick={clickOutsideActive ? handleClickOutside : undefined}
              className="fixed left-0 top-0 h-full w-full z-[1000] bg-transparent"
            />
          )}
        </span>
      </Tippy>
    </>
  );
};

export default Tooltip;
