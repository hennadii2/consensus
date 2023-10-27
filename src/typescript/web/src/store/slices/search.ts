import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { ISearchItem, SummaryResponse, YesNoResponse } from "helpers/api";
import { defaultMeterFilter } from "helpers/meterFilter";
import { MeterFilterParams } from "types/MeterFilterParams";

interface QueryData {
  searchId?: string;
  nuanceRequired?: boolean;
  isYesNoQuestion?: boolean;
  canSynthesize?: boolean;
  canSynthesizeSucceed?: boolean;
  numRelevantResults?: number;
  numTopResults?: number;
  isEnd?: boolean;
}

const defaultQueryData: QueryData = {
  searchId: undefined,
  canSynthesize: undefined,
  nuanceRequired: undefined,
  isYesNoQuestion: undefined,
  canSynthesizeSucceed: undefined,
};

interface SearchState {
  isSearching: boolean;
  isRefresh: boolean;
  isMeterRefresh: boolean;
  isEnd: boolean;
  results: ISearchItem[];
  page: number;
  meterFilter: MeterFilterParams;
  queryData: QueryData;
  yesNoData?: YesNoResponse;
  summaryData?: SummaryResponse;
}

const initialState = {
  isSearching: false,
  isRefresh: false,
  isMeterRefresh: false,
  isEnd: false,
  results: [],
  page: 0,
  meterFilter: defaultMeterFilter,
  queryData: defaultQueryData,
  yesNoData: undefined,
  summaryData: undefined,
} as SearchState;

const searchSlice = createSlice({
  name: "search",
  initialState,
  reducers: {
    setIsSearching(state: SearchState, { payload }: PayloadAction<boolean>) {
      state.isSearching = payload;
      if (payload) {
        state.results = [];
        state.queryData = defaultQueryData;
        state.yesNoData = undefined;
        state.summaryData = undefined;
        state.page = 0;
      }
    },
    setPage(state: SearchState, { payload }: PayloadAction<number>) {
      state.page = payload;
    },
    setIsRefresh(state: SearchState, { payload }: PayloadAction<boolean>) {
      state.isRefresh = payload;
    },
    setIsMeterRefresh(state: SearchState, { payload }: PayloadAction<boolean>) {
      state.isMeterRefresh = payload;
    },
    setIsEnd(state: SearchState, { payload }: PayloadAction<boolean>) {
      state.isEnd = payload;
    },
    setMeterFilter(
      state: SearchState,
      { payload }: PayloadAction<MeterFilterParams>
    ) {
      state.meterFilter = payload;
    },
    setQueryResultData(
      state: SearchState,
      { payload }: PayloadAction<QueryData>
    ) {
      state.queryData = payload;
    },
    setYesNoData(
      state: SearchState,
      { payload }: PayloadAction<YesNoResponse>
    ) {
      state.yesNoData = payload;
    },
    setSummaryData(
      state: SearchState,
      { payload }: PayloadAction<SummaryResponse>
    ) {
      state.summaryData = payload;
    },
  },
});

export const {
  setIsSearching,
  setPage,
  setIsRefresh,
  setIsMeterRefresh,
  setIsEnd,
  setMeterFilter,
  setQueryResultData,
  setYesNoData,
  setSummaryData,
} = searchSlice.actions;
export default searchSlice.reducer;
