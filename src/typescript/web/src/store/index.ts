import { Action, configureStore, ThunkAction } from "@reduxjs/toolkit";
import analytic from "./slices/analytic";
import bookmark from "./slices/bookmark";
import search from "./slices/search";
import setting from "./slices/setting";
import subscription from "./slices/subscription";

export const store = configureStore({
  reducer: {
    search,
    analytic,
    setting,
    subscription,
    bookmark,
  },
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;
