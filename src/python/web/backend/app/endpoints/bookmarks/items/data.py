from enum import Enum

from common.db.bookmark_items import BookmarkItem
from pydantic import BaseModel

LOG_ENDPOINT = "bookmark_items"


class LOG_EVENTS(Enum):
    DELETE_DB = "delete_from_db"
    READ_DB = "get_from_db"
    WRITE_DB = "write_to_db"


class BookMarkGetItemsResponse(BaseModel):
    """
    A response from the GET /bookmarks/items endpoint.
    """

    bookmark_items: dict[str, list[BookmarkItem]]


class BookmarkItemData(BaseModel):
    list_id: str
    search_url: str
    paper_id: str


class BookmarkCreateItemsRequest(BaseModel):
    items: list[BookmarkItemData]


class BookmarkCreateItemsResponse(BaseModel):
    """
    A response from the POST /bookmarks/items endpoint.
    """

    success: bool
    created_items: list[BookmarkItem]


class BookmarkDeleteItemResponse(BaseModel):
    """
    A response from the DELETE /bookmarks/items/:id endpoint.
    """

    id: str
    success: bool
