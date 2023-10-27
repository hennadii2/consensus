import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface SettingState {
  isMobile: boolean;
}

const initialState: SettingState = {
  isMobile: false,
};

const settingSlice = createSlice({
  name: "setting",
  initialState,
  reducers: {
    setSettingIsMobile(
      state: SettingState,
      { payload }: PayloadAction<boolean>
    ) {
      state.isMobile = payload;
    },
  },
});

export const { setSettingIsMobile } = settingSlice.actions;
export default settingSlice.reducer;
