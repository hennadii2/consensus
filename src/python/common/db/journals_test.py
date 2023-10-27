from datetime import datetime

import pytest  # type: ignore
from common.db.journals import JOURNALS_TABLE, Journals, journal_name_hash
from common.db.test.connect import MainDbTestClient
from journal_pb2 import Journal
from psycopg2.errors import UniqueViolation


@pytest.fixture
def connection():
    with MainDbTestClient() as connection:
        yield connection


def test_write_journal_succeeds(connection) -> None:
    timestamp = datetime.now()
    fmt = "%y%m%d%H%M%S"

    journals = Journals(connection)
    journal = journals.write_journal(
        name="Test Journal",
        print_issn=None,
        electronic_issn=None,
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {JOURNALS_TABLE}")
        results = cursor.fetchall()

        assert len(results) == 1

        actual = results[0]

        assert actual["id"] == journal.id
        assert actual["name"] == "Test Journal"
        assert actual["name_hash"] == journal_name_hash("Test Journal")
        assert actual["print_issn"] is None
        assert actual["electronic_issn"] is None
        assert actual["created_at"].strftime(fmt) == timestamp.strftime(fmt)
        assert actual["created_by"] == "test_job"
        assert actual["last_updated_at"].strftime(fmt) == timestamp.strftime(fmt)
        assert actual["last_updated_by"] == "test_job"


def test_write_journal_fails_if_name_already_exists(connection) -> None:
    timestamp = datetime.now()
    name = "Test Journal"

    journals = Journals(connection)
    journals.write_journal(
        name=name,
        print_issn=None,
        electronic_issn=None,
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )

    with pytest.raises(UniqueViolation, match="duplicate key value"):
        journals.write_journal(
            name=name,
            print_issn=None,
            electronic_issn=None,
            job_name="test_job",
            timestamp=timestamp,
            commit=True,
        )


def test_write_journal_succeeds_for_multiple_none_types_in_issn_fields(connection) -> None:
    timestamp = datetime.now()

    journals = Journals(connection)
    journals.write_journal(
        name="journal1",
        print_issn=None,
        electronic_issn=None,
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )
    journals.write_journal(
        name="journal2",
        print_issn=None,
        electronic_issn=None,
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )
    assert True


def test_write_journal_returns_expected_value(connection) -> None:
    timestamp = datetime.now()

    expected = Journal()
    expected.name = "name"
    expected.print_issn = "issn1"
    expected.electronic_issn = "issn2"

    journals = Journals(connection)
    actual = journals.write_journal(
        name="Test Journal",
        print_issn="issn1",
        electronic_issn="issn2",
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )

    actual == expected


def test_read_by_id_succeeds(connection) -> None:
    timestamp = datetime.now()

    expected = Journal()
    expected.name = "name"
    expected.print_issn = "issn1"
    expected.electronic_issn = "issn2"

    journal_id = None
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
             INSERT INTO {JOURNALS_TABLE} (
               name,
               name_hash,
               print_issn,
               electronic_issn,
               created_at,
               created_by,
               last_updated_at,
               last_updated_by
             ) VALUES (
               %(name)s,
               %(name_hash)s,
               %(print_issn)s,
               %(electronic_issn)s,
               %(created_at)s,
               %(created_by)s,
               %(last_updated_at)s,
               %(last_updated_by)s
             )
             RETURNING id
            """,
            {
                "name": expected.name,
                "name_hash": journal_name_hash(expected.name),
                "print_issn": expected.print_issn,
                "electronic_issn": expected.electronic_issn,
                "created_at": timestamp,
                "created_by": "job_name",
                "last_updated_at": timestamp,
                "last_updated_by": "job_name",
            },
        )
        journal_id = cursor.fetchone()["id"]

    journals = Journals(connection)
    actual = journals.read_by_id(journal_id)
    expected.id = journal_id

    assert actual == expected


def test_read_by_name_succeeds(connection) -> None:
    timestamp = datetime.now()

    journals = Journals(connection)
    expected = journals.write_journal(
        name="Test Journal",
        print_issn=None,
        electronic_issn=None,
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )
    actual = journals.read_by_name("test journal")
    assert actual == expected


def test_read_by_name_returns_none_for_unknown_journal(connection) -> None:
    journals = Journals(connection)
    actual = journals.read_by_name("unknown journal")
    assert actual is None


def test_read_by_name_returns_the_same_journal_for_the_same_normalized_name(connection) -> None:
    timestamp = datetime.now()

    name1 = "Test Journal"
    name2 = "test Journal"
    name3 = "Test Journal - version 1"

    journals = Journals(connection)
    journals.write_journal(
        name=name1,
        print_issn=None,
        electronic_issn=None,
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )

    actual1 = journals.read_by_name(name1)
    actual2 = journals.read_by_name(name2)
    actual3 = journals.read_by_name(name3)

    assert actual1 == actual2
    assert actual1 != actual3


def test_read_by_issn_succeeds(connection) -> None:
    timestamp = datetime.now()

    journals = Journals(connection)
    expected = journals.write_journal(
        name="Test Journal",
        print_issn="1234-5678",
        electronic_issn="8765-4321",
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )
    # Test print issn
    actual = journals.read_by_print_issn("1234-5678")
    assert actual == expected
    # Test electronic issn
    actual = journals.read_by_electronic_issn("8765-4321")
    assert actual == expected


def test_read_by_issn_fails_missing(connection) -> None:
    timestamp = datetime.now()

    journals = Journals(connection)
    _ = journals.write_journal(
        name="Test Journal",
        print_issn=None,
        electronic_issn=None,
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )
    # Test print issn
    actual = journals.read_by_print_issn("1234-5678")
    assert actual is None
    # Test electronic issn
    actual = journals.read_by_electronic_issn("8765-4321")
    assert actual is None


def test_read_by_issn_with_name_fallback_succeeds_with_issn(connection) -> None:
    timestamp = datetime.now()

    journals = Journals(connection)
    expected = journals.write_journal(
        name="Test Journal",
        print_issn="1234-5678",
        electronic_issn="8765-4321",
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )

    actual = journals.read_by_issn_with_name_fallback(
        issn_list=["1234-5678"], name="Test Journal 2"  # Only issn matches
    )
    assert actual == expected


def test_read_by_issn_with_name_fallback_succeeds_with_name_fallback(connection) -> None:
    timestamp = datetime.now()

    journals = Journals(connection)
    expected = journals.write_journal(
        name="Test Journal",
        print_issn="1234-5678",
        electronic_issn="8765-4321",
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )

    actual = journals.read_by_issn_with_name_fallback(
        issn_list=["1111-1111"], name="Test Journal"  # Only name matches
    )
    assert actual == expected


def test_read_by_issn_with_name_fallback_fails(connection) -> None:
    timestamp = datetime.now()

    journals = Journals(connection)
    _ = journals.write_journal(
        name="Test Journal",
        print_issn="1234-5678",
        electronic_issn="8765-4321",
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )

    actual = journals.read_by_issn_with_name_fallback(
        issn_list=["1111-1111"], name="Test Journal 2"  # Neither matches
    )
    assert actual is None
