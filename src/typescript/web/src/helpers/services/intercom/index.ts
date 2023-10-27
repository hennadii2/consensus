import { INTERCOM_API_BASE, INTERCOM_APP_ID } from "constants/config";
import { SynthesizeToggleState } from "enums/meter";

declare global {
  interface Window {
    Intercom: any;
    intercomSettings: any;
    attachEvent: any;
  }
}

type IntercomOptions = {
  name?: string | null;
  email?: string;
  created_at?: Date | null;
  user_id?: string | null;
  user_hash?: string;
  Plan?: "Premium" | "Free";
  "Billing Period"?: "Annually" | "Monthly";
};

// Loads Intercom with the snippet
// This must be run before boot, it initializes window.Intercom
export const load = () => {
  // prettier-ignore
  // @ts-ignore
  (function(){var w=window;var ic=w.Intercom;if(typeof ic==="function"){ic('reattach_activator');ic('update',w.intercomSettings);}else{var d=document;var i=function(){i.c(arguments);};i.q=[];i.c=function(args){i.q.push(args);};w.Intercom=i;var l=function(){var s=d.createElement('script');s.type='text/javascript';s.async=true;s.src='https://widget.intercom.io/widget/' + INTERCOM_APP_ID;var x=d.getElementsByTagName('script')[0];x.parentNode.insertBefore(s, x);};if(document.readyState==='complete'){l();}else if(w.attachEvent){w.attachEvent('onload',l);}else{w.addEventListener('load',l,false);}}})();
};

// Initializes Intercom
export const boot = (options?: IntercomOptions): void => {
  if (window && window.Intercom) {
    window.Intercom("boot", {
      app_id: INTERCOM_APP_ID,
      api_base: INTERCOM_API_BASE,
      ...options,
    });
  }
};

export const update = (options?: IntercomOptions): void => {
  if (window && window.Intercom) {
    window.Intercom("update", options);
  }
};

export const shutdown = (): void => {
  if (window && window.Intercom) {
    window.Intercom("shutdown");
  }
};

export const show = (): void => {
  if (window && window.Intercom) {
    window.Intercom("show");
  }
};

export const logSearchEvent = (
  query: string,
  isSynthesizeOn: SynthesizeToggleState = SynthesizeToggleState.ON
): void => {
  if (window && window.Intercom) {
    window.Intercom("trackEvent", "Search", {
      query,
      synthesize_state: isSynthesizeOn,
    });
  }
};
