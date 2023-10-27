from typing import Dict, List, Union

from common.db.bookmark_items import BookmarkItem, PaperBookmark, SearchBookmark
from web.backend.app.endpoints.bookmarks.items.data import BookmarkItemData


def create_bookmark_data(data: BookmarkItemData) -> Union[PaperBookmark, SearchBookmark]:
    if len(data.search_url) > 0:
        return SearchBookmark(search_url=data.search_url)
    elif len(data.paper_id) > 0:
        return PaperBookmark(paper_id=data.paper_id)
    else:
        raise ValueError(f"Failed to create_bookmark_data: invalid {data}")


def filter_duplicates(
    bookmarkItems: Dict[str, List[BookmarkItem]]
) -> Dict[str, List[BookmarkItem]]:
    """After migrating from claims to papers, bookmarks no longer contain claim_ids. Some lists
    have multiple claims that point to the same paper, so we need to filter them out so that the
    new paper-based bookmarks lists do not contain duplicates."""
    filtered_dict = {}

    for key, bookmarks in bookmarkItems.items():
        seen = set()
        filtered_bookmarks = []

        for bookmark in bookmarks:
            if isinstance(bookmark.bookmark_data, PaperBookmark):
                identifier = (bookmark.bookmark_list_id, bookmark.bookmark_data.paper_id)

                if identifier not in seen:
                    seen.add(identifier)
                    filtered_bookmarks.append(bookmark)
            else:
                filtered_bookmarks.append(bookmark)  # For non-PaperBookmark items

        filtered_dict[key] = filtered_bookmarks

    return filtered_dict
