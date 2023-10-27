import { BOOKMARK_LISTNAME_FAVORITE } from "constants/config";
import {
  BookmarkItemsType,
  BookmarkSaveSearchState,
} from "store/slices/bookmark";

export enum BookmarkType {
  PAPER = "paper",
  SEARCH = "search",
}

export interface IBookmarkListItem {
  id: string;
  text_label: string;
  created_at: string;
  deleted_at: string;
}

export interface IBookmarkListResponse {
  clerk_user_id: string;
  bookmark_lists: IBookmarkListItem[];
}

export interface IBookmarkCreateListResponse {
  success: boolean;
  created_item: IBookmarkListItem;
}

export interface IBookmarkUpdateListResponse {
  success: boolean;
  updated_item: IBookmarkListItem;
}

export interface IBookmarkDeleteListResponse {
  id: string;
  success: boolean;
}

export interface IPaperBookmark {
  paper_id: string;
}

export interface ISearchBookmark {
  search_url: string;
}

export interface IBookmarkItem {
  id: number;
  clerk_user_id: string;
  bookmark_list_id: number;
  bookmark_type: BookmarkType;
  bookmark_data: IPaperBookmark | ISearchBookmark;
  created_at: string;
  deleted_at?: string;
}

export interface IBookmarkItemsResponse {
  bookmark_items: { [key: number]: IBookmarkItem[] };
}

export interface IBookmarkCreateItemData {
  list_id: string;
  search_url: string;
  paper_id: string;
}

export interface IBookmarkCreateItemsResponse {
  success: boolean;
  created_items: IBookmarkItem[];
}

export interface IBookmarkDeleteItemResponse {
  id: string;
  success: boolean;
}

export function sortBookMarkList(
  bookmarkLists: IBookmarkListItem[]
): IBookmarkListItem[] {
  bookmarkLists.sort((a: IBookmarkListItem, b: IBookmarkListItem) => {
    if (a.text_label == BOOKMARK_LISTNAME_FAVORITE) return -1;
    if (b.text_label == BOOKMARK_LISTNAME_FAVORITE) return 1;

    const dateA = new Date(a.created_at as string);
    const dateB = new Date(b.created_at as string);
    return dateA.getTime() < dateB.getTime() ? 1 : -1;
  });
  return bookmarkLists;
}

export function findBookmarkItem(
  saveSearchState: BookmarkSaveSearchState,
  listId: string,
  bookmark_items: BookmarkItemsType
): IBookmarkItem | null {
  if (!bookmark_items || bookmark_items.hasOwnProperty(listId) == false)
    return null;

  const items: IBookmarkItem[] = bookmark_items[listId];
  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    if (
      saveSearchState.bookmarkType == BookmarkType.SEARCH &&
      item.bookmark_type == BookmarkType.SEARCH
    ) {
      const data: ISearchBookmark = item.bookmark_data as ISearchBookmark;
      if (data.search_url == saveSearchState.searchUrl) {
        return item;
      }
    } else if (
      saveSearchState.bookmarkType == BookmarkType.PAPER &&
      item.bookmark_type == BookmarkType.PAPER
    ) {
      const data: IPaperBookmark = item.bookmark_data as IPaperBookmark;
      if (data.paper_id == saveSearchState.paperId) {
        return item;
      }
    }
  }
  return null;
}

export function isSearchUrlBookMarked(
  search_url: string,
  bookmark_items: BookmarkItemsType
): boolean {
  let isBookmarked = false;
  for (const key in bookmark_items) {
    const items: IBookmarkItem[] = bookmark_items[key];
    items.forEach((item) => {
      if (item.bookmark_type == BookmarkType.SEARCH) {
        const bookmarkData: ISearchBookmark =
          item.bookmark_data as ISearchBookmark;
        if (bookmarkData.search_url == search_url) {
          isBookmarked = true;
        }
      }
    });
  }

  return isBookmarked;
}

export function isPaperBookMarked(
  paper_id: string,
  bookmark_items: BookmarkItemsType
): boolean {
  let isBookmarked = false;
  for (const key in bookmark_items) {
    const items: IBookmarkItem[] = bookmark_items[key];
    items.forEach((item) => {
      if (item.bookmark_type == BookmarkType.PAPER) {
        const bookmarkData: IPaperBookmark =
          item.bookmark_data as IPaperBookmark;
        if (bookmarkData.paper_id == paper_id) {
          isBookmarked = true;
        }
      }
    });
  }

  return isBookmarked;
}

export function getPaperSearchNum(
  list_id: string,
  bookmark_items: BookmarkItemsType
): {
  paperNum: number;
  searchNum: number;
} {
  let paperNum = 0;
  let searchNum = 0;
  if (bookmark_items && bookmark_items.hasOwnProperty(list_id)) {
    const items: IBookmarkItem[] = bookmark_items[list_id];

    items.forEach((item) => {
      if (item.bookmark_type == BookmarkType.PAPER) {
        paperNum++;
      } else if (item.bookmark_type == BookmarkType.SEARCH) {
        searchNum++;
      }
    });
  }

  return {
    paperNum: paperNum,
    searchNum: searchNum,
  };
}

export function hasBookmarkListItemsDifference(
  bookmarkItems1: IBookmarkItem[],
  bookmarkItems2: IBookmarkItem[]
): boolean {
  let bookmarkPaperCount1 = bookmarkItems1.filter(
    (x) => x.bookmark_type == BookmarkType.PAPER
  ).length;
  let bookmarkPaperCount2 = bookmarkItems2.filter(
    (x) => x.bookmark_type == BookmarkType.PAPER
  ).length;

  if (bookmarkPaperCount1 != bookmarkPaperCount2) {
    return true;
  }

  for (let i = 0; i < bookmarkItems1.length; i++) {
    const bookmarkItem1: IBookmarkItem = bookmarkItems1[i];
    if (bookmarkItem1.bookmark_type == BookmarkType.PAPER) {
      let isIncluded = false;
      for (let j = 0; j < bookmarkItems2.length; j++) {
        const bookmarkItem2: IBookmarkItem = bookmarkItems2[j];
        if (bookmarkItem2.bookmark_type == BookmarkType.PAPER) {
          const bookmarkData1: IPaperBookmark =
            bookmarkItem1.bookmark_data as IPaperBookmark;
          const bookmarkData2: IPaperBookmark =
            bookmarkItem2.bookmark_data as IPaperBookmark;

          if (bookmarkData1.paper_id == bookmarkData2.paper_id) {
            isIncluded = true;
            break;
          }
        }
      }
      if (isIncluded == false) {
        return true;
      }
    }
  }
  return false;
}

export function getBookmarkItemsCount(bookmark_items: {
  [key: number]: IBookmarkItem[];
}): number {
  let bookmarkItemNum = 0;
  for (let key in bookmark_items) {
    bookmarkItemNum += bookmark_items[key].length;
  }
  return bookmarkItemNum;
}
