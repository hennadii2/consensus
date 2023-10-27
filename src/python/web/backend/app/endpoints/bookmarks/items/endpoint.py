from common.db.bookmark_items import BookmarkItem, BookmarkItems, PaperBookmark
from common.db.db_connection_handler import is_unrecoverable_db_error
from common.db.hash_paper_ids import HashPaperIds
from common.logging.timing import time_endpoint_event
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from web.backend.app.common.auth import get_verified_clerk_user
from web.backend.app.endpoints.bookmarks.items.data import (
    LOG_ENDPOINT,
    LOG_EVENTS,
    BookmarkCreateItemsRequest,
    BookmarkCreateItemsResponse,
    BookmarkDeleteItemResponse,
    BookMarkGetItemsResponse,
)
from web.backend.app.endpoints.bookmarks.items.util import create_bookmark_data, filter_duplicates
from web.backend.app.state import SharedState

router = APIRouter()


# Note: keep endpoint non-async until await is used to avoid blocking the main thread
# See https://github.com/Consensus-NLP/common/pull/1120
@router.get("/", response_model=BookMarkGetItemsResponse)
def bookmark_get_items(
    request: Request,
) -> BookMarkGetItemsResponse:
    shared: SharedState = request.app.state.shared
    db = shared.db()
    bookmark_items = BookmarkItems(db.connection)
    hash_paper_ids = HashPaperIds(db.connection)

    clerk_user = get_verified_clerk_user(request=request, env=shared.config.auth_env)
    clerk_user_id = ""

    try:
        if clerk_user is None:
            raise ValueError("Unauthed bookmark missing clerk token")

        clerk_user_id = clerk_user.user_id
        log_read_bookmark_items_from_db_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.READ_DB.value,
        )

        bookmarks_dict = bookmark_items.read_by_clerk_customer_id(clerk_user_id)
        if bookmarks_dict is not None:
            bookmarks_dict = filter_duplicates(bookmarks_dict)

            for bookmarks in bookmarks_dict.values():
                for bookmark in bookmarks:
                    if isinstance(bookmark.bookmark_data, PaperBookmark):
                        # Replace paper_id with hash_paper_id before sending to FE
                        paper_id = bookmark.bookmark_data.paper_id
                        hash_paper_id = hash_paper_ids.read_hash_paper_id(paper_id)
                        if hash_paper_id is None:
                            raise ValueError(
                                "Failed to read bookmark item: missing hash_paper_id: {paper_id}"
                            )
                        bookmark.bookmark_data.paper_id = hash_paper_id

        response = BookMarkGetItemsResponse(bookmark_items=bookmarks_dict)

        log_read_bookmark_items_from_db_timing_event()

        return response
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()

        logger.exception(f"Failed to get bookmark list items for: clerk_user_id={clerk_user_id}")
        raise HTTPException(status_code=500, detail=str(e))


# Note: keep endpoint non-async until await is used to avoid blocking the main thread
# See https://github.com/Consensus-NLP/common/pull/1120
@router.post("/", response_model=BookmarkCreateItemsResponse)
def bookmark_create_items(
    request: Request,
    data: BookmarkCreateItemsRequest,
) -> BookmarkCreateItemsResponse:
    shared: SharedState = request.app.state.shared
    db = shared.db()
    bookmark_items = BookmarkItems(db.connection)
    hash_paper_ids = HashPaperIds(db.connection)

    clerk_user = get_verified_clerk_user(request=request, env=shared.config.auth_env)
    clerk_user_id = ""

    try:
        if clerk_user is None:
            raise ValueError("Failed to create bookmark item: missing clerk token")
        clerk_user_id = clerk_user.user_id

        log_create_bookmark_item_to_db_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.WRITE_DB.value,
        )
        created_items: list[BookmarkItem] = []
        for item_data in data.items:
            bookmark_data = create_bookmark_data(item_data)

            hash_paper_id = None
            if isinstance(bookmark_data, PaperBookmark):
                # Replace hash_paper_id with paper_id to keep DB consistent
                hash_paper_id = bookmark_data.paper_id
                paper_id = hash_paper_ids.read_paper_id(hash_paper_id)
                if paper_id is None:
                    raise ValueError(
                        "Failed to create bookmark item: missing paper_id: {hash_paper_id}"
                    )
                bookmark_data.paper_id = paper_id

            created_item = bookmark_items.write_bookmark(
                clerk_user_id=clerk_user_id,
                bookmark_list_id=item_data.list_id,
                bookmark_data=bookmark_data,
                commit=True,
            )

            if isinstance(created_item.bookmark_data, PaperBookmark) and hash_paper_id:
                # Re-replace hash_paper_id before sending bookmark back to FE
                created_item.bookmark_data.paper_id = hash_paper_id

            created_items.append(created_item)
        log_create_bookmark_item_to_db_timing_event()

        return BookmarkCreateItemsResponse(success=True, created_items=created_items)
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()

        logger.exception(f"Failed to create bookmark list items for: {clerk_user_id}")
        raise HTTPException(status_code=500, detail=str(e))


# Note: keep endpoint non-async until await is used to avoid blocking the main thread
# See https://github.com/Consensus-NLP/common/pull/1120
@router.delete("/{id}", response_model=BookmarkDeleteItemResponse)
def bookmark_delete_item(
    request: Request,
    id: str,
) -> BookmarkDeleteItemResponse:
    shared: SharedState = request.app.state.shared
    db = shared.db()
    bookmark_items = BookmarkItems(db.connection)

    clerk_user = get_verified_clerk_user(request=request, env=shared.config.auth_env)

    try:
        if clerk_user is None:
            raise ValueError("Failed to get delete bookmark item: missing clerk token")

        log_delete_bookmark_item_from_db_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.DELETE_DB.value,
        )
        bookmark_items.delete_bookmark_by_id(id=int(id), commit=True)

        log_delete_bookmark_item_from_db_timing_event()

        return BookmarkDeleteItemResponse(
            id=id,
            success=True,
        )
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()

        logger.exception(
            f"""Failed to delete bookmark item for:
            id={id}"""
        )
        raise HTTPException(status_code=500, detail=str(e))
