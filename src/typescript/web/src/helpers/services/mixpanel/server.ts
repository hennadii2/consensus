import { strict as assert } from "assert";
import { MIXPANEL_API_KEY } from "constants/config";
import Mixpanel from "mixpanel";
import { MixpanelEvent, SignUpEvent, TrackEventData } from "./events";

type ServerSideMixpanel = typeof Mixpanel;

/** Returns initialized Mixpanel, which can only be called server side. */
let SERVER_SIDE_MIXPANEL_SINGLETON: ServerSideMixpanel | null = null;
export function getMixpanelSingelton(): ServerSideMixpanel {
  if (!SERVER_SIDE_MIXPANEL_SINGLETON) {
    assert(MIXPANEL_API_KEY);
    SERVER_SIDE_MIXPANEL_SINGLETON = Mixpanel.init(MIXPANEL_API_KEY);
  }
  return SERVER_SIDE_MIXPANEL_SINGLETON;
}

/** User completes sign up. */
export function trackSignUpEvent(userId: string, data: SignUpEvent) {
  const mixpanel = getMixpanelSingelton();
  mixpanel.people.set(userId, {
    $name: userId,
    signUpDate: data.createdAt ? new Date(data.createdAt).toISOString() : null,
    signUpAuthMethod: data.authMethod || null,
  });
  mixpanel.track(MixpanelEvent.SignUp, {
    distinct_id: userId,
    authMethod: data.authMethod || null,
  });
}

/** User tracks a standard event. */
export function trackEvent(userId: string | null, data: TrackEventData) {
  const mixpanel = getMixpanelSingelton();
  const { event, ...eventData } = data;
  assert(Object.values(MixpanelEvent).includes(event));
  const eventDataDict = eventData as { [key: string]: any };
  eventDataDict["distinct_id"] = userId;
  mixpanel.track(event, eventDataDict);
}
