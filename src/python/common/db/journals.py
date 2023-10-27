from __future__ import annotations

import uuid
from collections import OrderedDict
from datetime import datetime, timezone
from typing import Any, Iterator, Optional

import psycopg2
from journal_pb2 import Journal

JOURNALS_TABLE = "journals"
JOURNALS_COLUMN_ID = "id"
JOURNALS_COLUMN_NAME = "name"
JOURNALS_COLUMN_NAME_HASH = "name_hash"
JOURNALS_COLUMN_PRINT_ISSN = "print_issn"
JOURNALS_COLUMN_ELECTRONIC_ISSN = "electronic_issn"
JOURNALS_COLUMN_CREATED_AT = "created_at"
JOURNALS_COLUMN_CREATED_BY = "created_by"
JOURNALS_COLUMN_LAST_UPDATED_AT = "last_updated_at"
JOURNALS_COLUMN_LAST_UPDATED_BY = "last_updated_by"


def journals_row_to_proto(row: Any) -> Journal:
    journal = Journal()
    journal.id = row[JOURNALS_COLUMN_ID]
    journal.name = row[JOURNALS_COLUMN_NAME]

    print_issn = row[JOURNALS_COLUMN_PRINT_ISSN]
    if print_issn:
        journal.print_issn = print_issn

    electronic_issn = row[JOURNALS_COLUMN_ELECTRONIC_ISSN]
    if electronic_issn:
        journal.electronic_issn = electronic_issn

    return journal


def journal_name_hash(name: str) -> str:
    NAMESPACE_JOURNAL_NAME = uuid.NAMESPACE_DNS
    normalized = name.lower()
    return uuid.uuid5(NAMESPACE_JOURNAL_NAME, normalized).hex


class Journals:
    """
    Interface class for reading/writing journals stored in a DB.
    """

    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def read_all(self) -> Iterator[Journal]:
        """Reads all rows in the journals table using a server side cursor."""

        sql = f""" SELECT * FROM {JOURNALS_TABLE} """
        with self.connection.cursor("server_side_cursor") as cursor:
            cursor.execute(sql)
            for row in cursor:
                journal = journals_row_to_proto(row)
                yield journal

    def write_journal(
        self,
        name: str,
        print_issn: Optional[str],
        electronic_issn: Optional[str],
        job_name: str,
        timestamp: Optional[datetime] = None,
        commit=False,
    ) -> Journal:
        """
        Writes a journal to the database with a newly generated ID.

        Raises:
            ValueError: if journal with the same name or ISSN already exists
        """

        if not timestamp:
            timestamp = datetime.now(timezone.utc)

        sql = f"""
          INSERT INTO {JOURNALS_TABLE} (
            {JOURNALS_COLUMN_NAME},
            {JOURNALS_COLUMN_NAME_HASH},
            {JOURNALS_COLUMN_PRINT_ISSN},
            {JOURNALS_COLUMN_ELECTRONIC_ISSN},
            {JOURNALS_COLUMN_CREATED_AT},
            {JOURNALS_COLUMN_CREATED_BY},
            {JOURNALS_COLUMN_LAST_UPDATED_AT},
            {JOURNALS_COLUMN_LAST_UPDATED_BY}
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
          RETURNING {JOURNALS_COLUMN_ID}
        """
        data = {
            "name": name,
            "name_hash": journal_name_hash(name),
            "print_issn": print_issn,
            "electronic_issn": electronic_issn,
            "created_at": timestamp,
            "created_by": job_name,
            "last_updated_at": timestamp,
            "last_updated_by": job_name,
        }

        journal = Journal()
        journal.name = name
        if print_issn:
            journal.print_issn = print_issn
        if electronic_issn:
            journal.electronic_issn = electronic_issn

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            journal.id = cursor.fetchone()[JOURNALS_COLUMN_ID]

        if commit:
            self.connection.commit()

        return journal

    def read_by_id(self, journal_id: int) -> Optional[Journal]:
        """
        Returns a journal from the database for the ID, or None if not found.

        Raises:
            ValueError: if more than 1 journal is found
        """

        sql = f"""
          SELECT * FROM {JOURNALS_TABLE}
            WHERE {JOURNALS_COLUMN_ID} = %(id)s
        """
        data = {"id": journal_id}
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            if not len(results):
                return None
            if len(results) > 1:
                raise ValueError(
                    "Failed to read journal by id: found {} results, expected 1".format(
                        len(results)
                    )
                )
            row = results[0]
            journal = journals_row_to_proto(row)
            return journal

    def _read_by_name_or_issn(
        self,
        column_name: str,
        column_value: str,
    ) -> Optional[Journal]:
        """
        Returns a journal from the database if a match for a column valus is found.

        Raises:
            ValueError: if more than 1 journal is found
        """

        valid_name_or_issn_columns = [
            JOURNALS_COLUMN_ELECTRONIC_ISSN,
            JOURNALS_COLUMN_PRINT_ISSN,
            JOURNALS_COLUMN_NAME_HASH,
        ]

        if column_name not in valid_name_or_issn_columns:
            raise ValueError(f"Invalid column to search: {column_name}")

        sql = f"""
          SELECT * FROM {JOURNALS_TABLE}
            WHERE {column_name} = %(column_value)s
        """
        data = {"column_value": column_value}
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            if not len(results):
                return None
            if len(results) > 1:
                raise ValueError(
                    f"""Failed to read journal by {column_name}:
                    found {len(results)} results, expected 1
                    """
                )
            row = results[0]
            journal = journals_row_to_proto(row)
            return journal

    def read_by_name(self, journal_name: str) -> Optional[Journal]:
        """
        Returns a journal from the database if a match for a normalized version of
        the journal name is found or returns None.

        Raises:
            ValueError: if more than 1 journal is found
        """
        return self._read_by_name_or_issn(
            JOURNALS_COLUMN_NAME_HASH,
            journal_name_hash(journal_name),
        )

    def read_by_print_issn(self, print_issn: str) -> Optional[Journal]:
        """
        Returns a journal from the database if a match for print issn is found.

        Raises:
            ValueError: if more than 1 journal is found
        """
        return self._read_by_name_or_issn(JOURNALS_COLUMN_PRINT_ISSN, print_issn)

    def read_by_electronic_issn(self, e_issn: str) -> Optional[Journal]:
        """
        Returns a journal from the database if a match for electronic issn is found.

        Raises:
            ValueError: if more than 1 journal is found
        """
        return self._read_by_name_or_issn(JOURNALS_COLUMN_ELECTRONIC_ISSN, e_issn)

    def read_by_issn_with_name_fallback(self, issn_list: list[str], name: str) -> Any:
        """
        Reads a journal from the database by issn; if not found, reads by name.

        Returns None if not found.
        """
        # Use OrderedDict to dedupe and preserve order.
        for issn in OrderedDict.fromkeys(issn_list).keys():
            # TODO: add a print/electronic issn combined sql query to reduce reads
            # Try print issn first
            journal = self.read_by_print_issn(print_issn=issn)
            if not journal:
                # Fallback to electronic issn
                journal = self.read_by_electronic_issn(e_issn=issn)

            if journal:
                break
        else:
            # If no issn is matched, fallback to journal name
            journal = self.read_by_name(journal_name=name)

        return journal
