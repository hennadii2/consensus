import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import {
  BookmarkType,
  IBookmarkItem,
  IBookmarkListItem,
  sortBookMarkList,
} from "helpers/bookmark";

export interface BookmarkSaveSearchState {
  bookmarkType: BookmarkType;
  searchUrl: string;
  paperId: string;
}

export type BookmarkItemsType = {
  [key: string]: IBookmarkItem[];
};

interface BookmarkState {
  bookmarkLists: IBookmarkListItem[];
  bookmarkItems: BookmarkItemsType;
  isBookmarkListLoaded: boolean | undefined;
  isBookmarkItemsLoaded: boolean | undefined;
  selectedListIds: string[];
  bookmarkSaveSearchState: BookmarkSaveSearchState;
  isLimitedBookmarkList: boolean | undefined;
  isLimitedBookmarkItem: boolean | undefined;
}

const initialState = {
  bookmarkLists: [],
  bookmarkItems: {} as BookmarkItemsType,
  isBookmarkListLoaded: undefined,
  isBookmarkItemsLoaded: undefined,
  selectedListIds: [],
  bookmarkSaveSearchState: {
    bookmarkType: BookmarkType.PAPER,
    searchUrl: "",
    paperId: "",
  },
  isLimitedBookmarkList: undefined,
  isLimitedBookmarkItem: undefined,
} as BookmarkState;

const bookmarkSlice = createSlice({
  name: "bookmark",
  initialState,
  reducers: {
    setBookmarkLists(
      state: BookmarkState,
      { payload }: PayloadAction<IBookmarkListItem[]>
    ) {
      state.bookmarkLists = sortBookMarkList(payload);
      state.isBookmarkListLoaded = true;
    },

    addBookmarkList(
      state: BookmarkState,
      { payload }: PayloadAction<IBookmarkListItem>
    ) {
      state.bookmarkLists.push(payload);
      state.bookmarkLists = sortBookMarkList(state.bookmarkLists);
    },

    updateBookmarkList(
      state: BookmarkState,
      { payload }: PayloadAction<IBookmarkListItem>
    ) {
      for (let i = 0; i < state.bookmarkLists.length; i++) {
        if (state.bookmarkLists[i].id == payload.id) {
          state.bookmarkLists[i] = payload;
          break;
        }
      }
    },

    removeBookmarkList(
      state: BookmarkState,
      { payload }: PayloadAction<string>
    ) {
      let existingList: IBookmarkListItem | null = null;
      for (let i = 0; i < state.bookmarkLists.length; i++) {
        if (state.bookmarkLists[i].id == payload) {
          existingList = state.bookmarkLists[i];
          break;
        }
      }

      if (existingList != null) {
        const index = state.bookmarkLists.indexOf(existingList);
        if (index > -1) {
          state.bookmarkLists.splice(index, 1);
        }
      }
    },

    resetCheckList(state: BookmarkState) {
      state.selectedListIds = [];
    },

    checkList(state: BookmarkState, { payload }: PayloadAction<string>) {
      if (state.selectedListIds.includes(payload) == false) {
        state.selectedListIds.push(payload);
      }
    },

    uncheckList(state: BookmarkState, { payload }: PayloadAction<string>) {
      const index = state.selectedListIds.indexOf(payload, 0);
      if (index > -1) {
        state.selectedListIds.splice(index, 1);
      }
    },

    setBookmarkItems(
      state: BookmarkState,
      { payload }: PayloadAction<{ [key: number]: IBookmarkItem[] }>
    ) {
      state.bookmarkItems = payload;
      state.isBookmarkItemsLoaded = true;
    },

    addBookmarkItem(
      state: BookmarkState,
      { payload }: PayloadAction<IBookmarkItem>
    ) {
      const listId = payload.bookmark_list_id;
      let items: IBookmarkItem[] = [];
      if (state.bookmarkItems.hasOwnProperty(listId)) {
        items = state.bookmarkItems[listId];
      }

      let isExist = false;
      for (let i = 0; i < items.length; i++) {
        if (items[i].id == payload.id) {
          isExist = true;
          break;
        }
      }
      if (isExist == false) {
        items.push(payload);
        state.bookmarkItems[listId] = items;
      }
    },

    removeBookmarkItem(
      state: BookmarkState,
      { payload }: PayloadAction<IBookmarkItem>
    ) {
      const listId = payload.bookmark_list_id;
      let items: IBookmarkItem[] = [];
      if (state.bookmarkItems.hasOwnProperty(listId)) {
        items = state.bookmarkItems[listId];
      }

      let existingItem: IBookmarkItem | null = null;
      for (let i = 0; i < items.length; i++) {
        if (items[i].id == payload.id) {
          existingItem = items[i];
          break;
        }
      }

      if (existingItem != null) {
        const index = items.indexOf(existingItem);
        if (index > -1) {
          items.splice(index, 1);
        }
        state.bookmarkItems[listId] = items;
      }
    },

    setBookmarkSaveSearchState(
      state: BookmarkState,
      { payload }: PayloadAction<BookmarkSaveSearchState>
    ) {
      state.bookmarkSaveSearchState = payload;
    },

    setIsLimitedBookmarkList(
      state: BookmarkState,
      { payload }: PayloadAction<boolean>
    ) {
      state.isLimitedBookmarkList = payload;
    },

    setIsLimitedBookmarkItem(
      state: BookmarkState,
      { payload }: PayloadAction<boolean>
    ) {
      state.isLimitedBookmarkItem = payload;
    },
  },
});

export const {
  setBookmarkLists,
  addBookmarkList,
  updateBookmarkList,
  removeBookmarkList,
  resetCheckList,
  checkList,
  uncheckList,
  setBookmarkItems,
  addBookmarkItem,
  removeBookmarkItem,
  setBookmarkSaveSearchState,
  setIsLimitedBookmarkList,
  setIsLimitedBookmarkItem,
} = bookmarkSlice.actions;
export default bookmarkSlice.reducer;
