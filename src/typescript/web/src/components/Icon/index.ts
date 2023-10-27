import dynamic from "next/dynamic";
import IconLoader from "./IconLoader/IconLoader";
import IconText, { IconTextProps } from "./IconText/IconText";

const Icon = dynamic(() => import("./Icon/Icon"), {
  ssr: false,
});

export { IconLoader, IconText };
export type { IconTextProps };

export default Icon;
