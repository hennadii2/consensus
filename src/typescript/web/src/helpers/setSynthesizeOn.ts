import { SynthesizeToggleState } from "enums/meter";
import { getCookie, setCookie } from "react-use-cookie";

export const setSynthesizeOn = () => {
  const currentSynthesize = getCookie("synthesize");
  if (currentSynthesize === "") {
    setCookie("synthesize", SynthesizeToggleState.ON);
  }
};
