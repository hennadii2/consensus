from common.db.bookmark_items import BookmarkItems
from common.db.bookmark_lists import BookmarkLists
from common.db.db_connection_handler import is_unrecoverable_db_error
from common.logging.timing import time_endpoint_event
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from web.backend.app.common.auth import get_verified_clerk_user
from web.backend.app.endpoints.bookmarks.lists.data import (
    LOG_ENDPOINT,
    LOG_EVENTS,
    BookmarkCreateListRequest,
    BookmarkCreateListResponse,
    BookmarkGetListsResponse,
    BookMarkUpdateListRequest,
    BookmarkUpdateListResponse,
    DeleteBookmarkListResponse,
)
from web.backend.app.state import SharedState

router = APIRouter()


# Note: keep endpoint non-async until await is used to avoid blocking the main thread
# See https://github.com/Consensus-NLP/common/pull/1120
@router.get("/", response_model=BookmarkGetListsResponse)
def bookmark_get_lists(
    request: Request,
    favorite_list_name: str,
) -> BookmarkGetListsResponse:
    shared: SharedState = request.app.state.shared
    db = shared.db()
    bookmark_lists = BookmarkLists(db.connection)

    clerk_user = get_verified_clerk_user(request=request, env=shared.config.auth_env)
    clerk_user_id = None

    try:
        if clerk_user is None:
            raise ValueError("Failed to get bookmark lists: missing clerk token")
        clerk_user_id = clerk_user.user_id

        if len(favorite_list_name) == 0:
            raise ValueError("Failed to get bookmark lists: empty favorite list name")

        log_read_bookmark_list_from_db_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.READ_DB.value,
        )
        lists = bookmark_lists.read_by_clerk_customer_id(clerk_user_id)
        log_read_bookmark_list_from_db_timing_event()

        if len(lists) <= 0:
            # Create favorite list if there are no existing lists
            favorite_list = bookmark_lists.create_bookmark_list(
                clerk_user_id=clerk_user_id,
                text_label=favorite_list_name,
                commit=True,
            )
            lists = [favorite_list]

        return BookmarkGetListsResponse(
            clerk_user_id=clerk_user_id,
            bookmark_lists=lists,
        )
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()

        logger.exception(f"Failed to run bookmark_get_lists for: clerk_user_id={clerk_user_id}")
        raise HTTPException(status_code=500, detail=str(e))


# Note: keep endpoint non-async until await is used to avoid blocking the main thread
# See https://github.com/Consensus-NLP/common/pull/1120
@router.post("/", response_model=BookmarkCreateListResponse)
def bookmark_create_list(
    request: Request,
    data: BookmarkCreateListRequest,
) -> BookmarkCreateListResponse:
    shared: SharedState = request.app.state.shared
    db = shared.db()
    bookmarkLists = BookmarkLists(db.connection)

    clerk_user = get_verified_clerk_user(request=request, env=shared.config.auth_env)
    clerk_user_id = ""

    try:
        if clerk_user is None:
            raise ValueError("Unauthed bookmark missing clerk token")

        clerk_user_id = clerk_user.user_id

        ret = False

        log_create_bookmark_list_to_db_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.WRITE_DB.value,
        )
        created_list = bookmarkLists.create_bookmark_list(
            clerk_user_id=clerk_user_id,
            text_label=data.text_label,
            commit=True,
        )

        log_create_bookmark_list_to_db_timing_event()
        ret = True

        logger.info(f"wrote_to_bookmark_list: {clerk_user_id} {ret}")
        response = BookmarkCreateListResponse(success=ret, created_item=created_list)

        return response
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()

        logger.exception(f"Failed to create bookmark list for: {clerk_user_id}")
        raise HTTPException(status_code=500, detail=str(e))


# Note: keep endpoint non-async until await is used to avoid blocking the main thread
# See https://github.com/Consensus-NLP/common/pull/1120
@router.put("/{id}", response_model=BookmarkUpdateListResponse)
def bookmark_update_list(
    request: Request,
    id: str,
    data: BookMarkUpdateListRequest,
) -> BookmarkUpdateListResponse:
    shared: SharedState = request.app.state.shared
    db = shared.db()
    bookmarkLists = BookmarkLists(db.connection)

    clerk_user = get_verified_clerk_user(request=request, env=shared.config.auth_env)
    clerk_user_id = ""

    try:
        if clerk_user is None:
            raise ValueError("Failed to update bookmark list: missing clerk token")
        clerk_user_id = clerk_user.user_id

        log_update_bookmark_list_to_db_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.WRITE_DB.value,
        )
        updated_list = bookmarkLists.update_bookmark_list(
            bookmark_list_id=id,
            new_text_label=data.text_label,
            commit=True,
        )
        log_update_bookmark_list_to_db_timing_event()

        response = BookmarkUpdateListResponse(
            success=True,
            updated_item=updated_list,
        )

        return response
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()

        logger.exception(
            f"""Failed to update bookmark list for:
            id={id}
            clerk_user_id={clerk_user_id}"""
        )
        raise HTTPException(status_code=500, detail=str(e))


# Note: keep endpoint non-async until await is used to avoid blocking the main thread
# See https://github.com/Consensus-NLP/common/pull/1120
@router.delete("/{id}", response_model=DeleteBookmarkListResponse)
def bookmark_delete_list(
    request: Request,
    id: str,
) -> DeleteBookmarkListResponse:
    shared: SharedState = request.app.state.shared
    db = shared.db()
    bookmarkLists = BookmarkLists(db.connection)
    bookmarkItems = BookmarkItems(db.connection)

    clerk_user = get_verified_clerk_user(request=request, env=shared.config.auth_env)

    try:
        if clerk_user is None:
            raise ValueError("Failed to get delete bookmark list: missing clerk token")

        log_delete_bookmark_list_from_db_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.DELETE_DB.value,
        )
        bookmarkLists.delete_bookmark_list(bookmark_list_id=id, commit=True)
        bookmarkItems.delete_bookmark_items_by_list_id(list_id=id, commit=True)
        log_delete_bookmark_list_from_db_timing_event()

        return DeleteBookmarkListResponse(
            id=id,
            success=True,
        )
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()

        logger.exception(
            f"""Failed to delete bookmark list for:
            id={id}"""
        )
        raise HTTPException(status_code=500, detail=str(e))
