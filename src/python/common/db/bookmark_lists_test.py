import pytest  # type: ignore
from common.db.bookmark_lists import BookmarkList, BookmarkLists
from common.db.test.connect import MainDbTestClient


@pytest.fixture
def connection():
    with MainDbTestClient() as connection:
        yield connection


def test_create_bookmark_list_to_new_user(connection) -> None:
    db = BookmarkLists(connection)

    actual = db.create_bookmark_list(
        clerk_user_id="user_1",
        text_label="default list",
        commit=True,
    )
    expected = BookmarkList(
        id=actual.id,
        text_label="default list",
        created_at=actual.created_at,
        deleted_at=None,
    )
    assert actual == expected


def test_create_bookmark_list_to_existing_user(connection) -> None:
    db = BookmarkLists(connection)

    db.create_bookmark_list(
        clerk_user_id="user_1",
        text_label="default list",
        commit=True,
    )
    actual = db.create_bookmark_list(
        clerk_user_id="user_1",
        text_label="another new lists",
        commit=True,
    )
    expected = BookmarkList(
        id=actual.id,
        text_label="another new lists",
        created_at=actual.created_at,
        deleted_at=None,
    )
    assert actual == expected


def test_read_by_unknown_customer_returns_none(connection) -> None:
    db = BookmarkLists(connection)
    bookmarks = db.read_by_clerk_customer_id(clerk_user_id="user_1")
    assert bookmarks == []


def test_read_by_known_customer_returns_bookmarks(connection) -> None:
    db = BookmarkLists(connection)
    list_1 = db.create_bookmark_list(
        clerk_user_id="user_1",
        text_label="list_1",
        commit=True,
    )
    list_2 = db.create_bookmark_list(
        clerk_user_id="user_1",
        text_label="list_2",
        commit=True,
    )
    bookmarks = db.read_by_clerk_customer_id(clerk_user_id="user_1")
    assert bookmarks == [list_2, list_1]


def test_update_bookmark_list_succeeds(connection) -> None:
    db = BookmarkLists(connection)
    original = db.create_bookmark_list(
        clerk_user_id="user_1",
        text_label="list_1",
        commit=True,
    )
    expected = BookmarkList(
        id=original.id,
        text_label="updated list_1",
        created_at=original.created_at,
        deleted_at=None,
    )
    assert original != expected

    actual_update = db.update_bookmark_list(
        bookmark_list_id=original.id,
        new_text_label=expected.text_label,
        commit=True,
    )
    assert actual_update == expected

    actual_read = db.read_by_id(bookmark_list_id=original.id)
    assert actual_read == expected


def test_update_bookmark_list_fails_for_unknown_id(connection) -> None:
    db = BookmarkLists(connection)

    with pytest.raises(ValueError, match="Failed update_bookmark_list: unknown id: unknown_id"):
        db.update_bookmark_list(
            bookmark_list_id="unknown_id",
            new_text_label="update will fail",
            commit=True,
        )


def test_delete_bookmark_list_succeeds(connection) -> None:
    db = BookmarkLists(connection)
    original = db.create_bookmark_list(
        clerk_user_id="user_1",
        text_label="list_1",
        commit=True,
    )
    actual_deleted = db.delete_bookmark_list(
        bookmark_list_id=original.id,
        commit=True,
    )
    expected = original
    expected.deleted_at = actual_deleted.deleted_at
    assert actual_deleted == expected

    actual_read = db.read_by_id(bookmark_list_id=original.id)
    assert actual_read is None


def test_delete_bookmark_list_fails_for_unknown_id(connection) -> None:
    db = BookmarkLists(connection)
    with pytest.raises(ValueError, match="Failed delete_bookmark_list: unknown id: unknown_id"):
        db.delete_bookmark_list(
            bookmark_list_id="unknown_id",
            commit=True,
        )
