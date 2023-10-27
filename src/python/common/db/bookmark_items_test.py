import pytest  # type: ignore
from common.db.bookmark_items import (
    BookmarkItem,
    BookmarkItems,
    BookmarkType,
    PaperBookmark,
    SearchBookmark,
)
from common.db.bookmark_lists import BookmarkLists
from common.db.test.connect import MainDbTestClient
from psycopg2.errors import ForeignKeyViolation

MOCK_USER_ID = "user_1"


@pytest.fixture
def connection():
    with MainDbTestClient() as connection:
        yield connection


def test_write_search_bookmark(connection) -> None:
    db = BookmarkItems(connection)
    bookmark_lists_db = BookmarkLists(connection)
    bookmark_list = bookmark_lists_db.create_bookmark_list(
        clerk_user_id=MOCK_USER_ID,
        text_label="test_list",
        commit=True,
    )

    search_url = "https://consensus.app/results/?q=does%20creatine%20help%20build%20muscle%3F%3F&synthesize=on"  # noqa: E501

    actual = db.write_bookmark(
        clerk_user_id=MOCK_USER_ID,
        bookmark_list_id=bookmark_list.id,
        bookmark_data=SearchBookmark(search_url=search_url),
        commit=True,
    )
    expected = BookmarkItem(
        id=1,
        clerk_user_id=MOCK_USER_ID,
        bookmark_list_id=bookmark_list.id,
        bookmark_type=BookmarkType.SEARCH,
        bookmark_data=SearchBookmark(search_url=search_url),
        created_at=actual.created_at,
        deleted_at=None,
    )
    assert actual == expected


def test_write_paper_bookmark(connection) -> None:
    db = BookmarkItems(connection)
    bookmark_lists_db = BookmarkLists(connection)
    bookmark_list = bookmark_lists_db.create_bookmark_list(
        clerk_user_id=MOCK_USER_ID,
        text_label="test_list",
        commit=True,
    )

    paper_id = "paper_id_1"

    actual = db.write_bookmark(
        clerk_user_id=MOCK_USER_ID,
        bookmark_list_id=bookmark_list.id,
        bookmark_data=PaperBookmark(paper_id=paper_id),
        commit=True,
    )
    expected = BookmarkItem(
        id=1,
        clerk_user_id=MOCK_USER_ID,
        bookmark_list_id=bookmark_list.id,
        bookmark_type=BookmarkType.PAPER,
        bookmark_data=PaperBookmark(paper_id=paper_id),
        created_at=actual.created_at,
        deleted_at=None,
    )
    assert actual == expected


def test_write_bookmark_fails_if_list_does_not_exist(connection) -> None:
    db = BookmarkItems(connection)

    search_url = "search_url"
    with pytest.raises(ForeignKeyViolation):
        db.write_bookmark(
            clerk_user_id=MOCK_USER_ID,
            bookmark_list_id="unknown_id",
            bookmark_data=SearchBookmark(search_url=search_url),
            commit=True,
        )


def test_read_by_clerk_customer_id(connection) -> None:
    db = BookmarkItems(connection)
    bookmark_lists_db = BookmarkLists(connection)

    bookmark_list_1 = bookmark_lists_db.create_bookmark_list(
        clerk_user_id=MOCK_USER_ID,
        text_label="test_list_1",
        commit=True,
    )
    bookmark_list_2 = bookmark_lists_db.create_bookmark_list(
        clerk_user_id=MOCK_USER_ID,
        text_label="test_list_2",
        commit=True,
    )

    paper_list1 = db.write_bookmark(
        clerk_user_id=MOCK_USER_ID,
        bookmark_list_id=bookmark_list_1.id,
        bookmark_data=PaperBookmark(paper_id="paper1"),
        commit=True,
    )
    search_list1 = db.write_bookmark(
        clerk_user_id=MOCK_USER_ID,
        bookmark_list_id=bookmark_list_1.id,
        bookmark_data=SearchBookmark(search_url="https://url_1"),
        commit=True,
    )

    paper_list2_1 = db.write_bookmark(
        clerk_user_id=MOCK_USER_ID,
        bookmark_list_id=bookmark_list_2.id,
        bookmark_data=PaperBookmark(paper_id="paper2"),
        commit=True,
    )
    paper_list2_2 = db.write_bookmark(
        clerk_user_id=MOCK_USER_ID,
        bookmark_list_id=bookmark_list_2.id,
        bookmark_data=PaperBookmark(paper_id="paper3"),
        commit=True,
    )

    expected = {}
    expected[bookmark_list_1.id] = [paper_list1, search_list1]
    expected[bookmark_list_2.id] = [paper_list2_1, paper_list2_2]

    actual = db.read_by_clerk_customer_id(MOCK_USER_ID)
    assert actual == expected


def test_delete_bookmark_items_by_list_id(connection) -> None:
    db = BookmarkItems(connection)
    bookmark_lists_db = BookmarkLists(connection)
    bookmark_list = bookmark_lists_db.create_bookmark_list(
        clerk_user_id=MOCK_USER_ID,
        text_label="test_list",
        commit=True,
    )

    search_url = "https://consensus.app/results/?q=does%20creatine%20help%20build%20muscle%3F%3F&synthesize=on"  # noqa: E501

    db.write_bookmark(
        clerk_user_id=MOCK_USER_ID,
        bookmark_list_id=bookmark_list.id,
        bookmark_data=SearchBookmark(search_url=search_url),
        commit=True,
    )

    db.delete_bookmark_items_by_list_id(list_id=bookmark_list.id, commit=True)

    actual = db.read_by_clerk_customer_id(MOCK_USER_ID)

    assert bool(actual) is False
