from enum import Enum

from common.db.bookmark_lists import BookmarkList
from pydantic import BaseModel

LOG_ENDPOINT = "bookmark_lists"


class LOG_EVENTS(Enum):
    DELETE_DB = "delete_from_db"
    READ_DB = "read_all_from_db"
    WRITE_DB = "create_to_db"
    UPDATE_DB = "update_to_db"


class BookmarkCreateListRequest(BaseModel):
    text_label: str
    # Bookmark list label string


class BookmarkCreateListResponse(BaseModel):
    """
    A response from the POST /bookmarks/lists endpoint.
    """

    success: bool
    created_item: BookmarkList


class BookMarkUpdateListRequest(BaseModel):
    text_label: str
    # Bookmark list label string


class BookmarkUpdateListResponse(BaseModel):
    """
    A response from the PUT /bookmarks/lists/:id endpoint.
    """

    success: bool
    updated_item: BookmarkList


class BookmarkGetListsResponse(BaseModel):
    """
    A response from the GET /bookmarks/lists endpoint.
    """

    clerk_user_id: str
    bookmark_lists: list[BookmarkList]


class DeleteBookmarkListResponse(BaseModel):
    """
    A response from the DELETE /bookmarks/lists/:id endpoint.
    """

    id: str
    # bookmark list Id
    success: bool
    # Success Status
