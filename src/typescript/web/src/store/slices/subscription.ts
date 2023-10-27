import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import {
  ISubscriptionData,
  ISubscriptionUsageData,
} from "helpers/subscription";

interface SubscriptionState {
  subscription: ISubscriptionData;
  usageData: ISubscriptionUsageData;
  isLoadedSubscription: boolean;
  isLoadedUsageData: boolean;
  useCredit: boolean | undefined;
  openUpgradeToPremiumPopup: boolean;
  products: any[];
}

const initialState = {
  subscription: { user: null, org: null },
  usageData: {
    creditUsageNum: 0,
    userCreatedDate: new Date().toISOString(),
    synthesizedQueries: [],
    studyPaperIds: [],
    isSet: false,
    stripeCustomerId: "",
  },
  isLoadedSubscription: false,
  isLoadedUsageData: false,
  useCredit: undefined,
  openUpgradeToPremiumPopup: false,
  products: [],
} as SubscriptionState;

const subscriptionSlice = createSlice({
  name: "subscription",
  initialState,
  reducers: {
    setSubscription(state: SubscriptionState, { payload }: PayloadAction<any>) {
      state.subscription = payload;
    },
    setSubscriptionUsageData(
      state: SubscriptionState,
      { payload }: PayloadAction<ISubscriptionUsageData>
    ) {
      state.usageData = payload;
    },
    setIsLoadedSubscription(
      state: SubscriptionState,
      { payload }: PayloadAction<boolean>
    ) {
      state.isLoadedSubscription = payload;
    },
    setIsLoadedUsageData(
      state: SubscriptionState,
      { payload }: PayloadAction<boolean>
    ) {
      state.isLoadedUsageData = payload;
    },
    setUseCredit(
      state: SubscriptionState,
      { payload }: PayloadAction<boolean>
    ) {
      state.useCredit = payload;
    },
    setCreditUsageNum(
      state: SubscriptionState,
      { payload }: PayloadAction<number>
    ) {
      state.usageData.creditUsageNum = payload;
    },
    increaseCreditUsageNum(state: SubscriptionState) {
      state.usageData.creditUsageNum++;
    },
    appendSynthesizedQuery(
      state: SubscriptionState,
      { payload }: PayloadAction<string>
    ) {
      if (!state.usageData.synthesizedQueries.includes(payload)) {
        state.usageData.synthesizedQueries.push(payload);
      }
    },
    appendStudyPaperId(
      state: SubscriptionState,
      { payload }: PayloadAction<string>
    ) {
      if (!state.usageData.studyPaperIds.includes(payload)) {
        state.usageData.studyPaperIds.push(payload);
      }
    },
    setOpenUpgradeToPremiumPopup(
      state: SubscriptionState,
      { payload }: PayloadAction<boolean>
    ) {
      state.openUpgradeToPremiumPopup = payload;
    },
    setProducts(state: SubscriptionState, { payload }: PayloadAction<any[]>) {
      state.products = payload;
    },
  },
});

export const {
  setSubscription,
  setSubscriptionUsageData,
  setIsLoadedSubscription,
  setIsLoadedUsageData,
  setCreditUsageNum,
  increaseCreditUsageNum,
  appendSynthesizedQuery,
  appendStudyPaperId,
  setUseCredit,
  setOpenUpgradeToPremiumPopup,
  setProducts,
} = subscriptionSlice.actions;
export default subscriptionSlice.reducer;
