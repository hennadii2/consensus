import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { IDetailItem } from "components/DetailContent/DetailContent";

export interface AnalyticUser {
  id: string;
  createdAt: string | null;
  lastSignInAt: string | null;
}

interface AnalyticState {
  query: string;
  page: number;
  index: number;
  item?: IDetailItem;
  user?: AnalyticUser;
}

const initialState = {
  query: "",
  page: 0,
  index: 0,
} as AnalyticState;

const analyticSlice = createSlice({
  name: "analytic",
  initialState,
  reducers: {
    setAnalyticMeta(
      state: AnalyticState,
      {
        payload,
      }: PayloadAction<{
        query: string;
        page: number;
        index: number;
      }>
    ) {
      state.page = payload.page;
      state.index = payload.index;
      state.query = payload.query;
    },
    setAnalyticItem(
      state: AnalyticState,
      { payload }: PayloadAction<IDetailItem | undefined>
    ) {
      state.item = payload;
    },
    setAnalyticUser(
      state: AnalyticState,
      { payload }: PayloadAction<AnalyticUser>
    ) {
      state.user = payload;
    },
  },
});

export const { setAnalyticMeta, setAnalyticItem, setAnalyticUser } =
  analyticSlice.actions;
export default analyticSlice.reducer;
