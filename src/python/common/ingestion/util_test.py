from __future__ import annotations

from common.ingestion.util import detect_language


def test_detect_language_uses_abstract_language_by_default() -> None:
    empty = ""
    unknown = "12345"
    english = "this is text in english"
    french = "voici un texte en français"

    actual = detect_language(title=english, abstract=french)
    assert actual == "fr"

    actual = detect_language(title=english, abstract=english)
    assert actual == "en"

    actual = detect_language(title=empty, abstract=english)
    assert actual == "en"

    actual = detect_language(title=unknown, abstract=english)
    assert actual == "en"


def test_detect_language_falls_back_to_title_language() -> None:
    empty = ""
    unknown = "12345"
    french = "voici un texte en français"

    actual = detect_language(title=french, abstract=empty)
    assert actual == "fr"

    actual = detect_language(title=french, abstract=unknown)
    assert actual == "fr"


def test_detect_language_returns_unknown_string_if_language_not_detected() -> None:
    empty = ""
    unknown = "12345"

    actual = detect_language(title=empty, abstract=empty)
    assert actual is None

    actual = detect_language(title=empty, abstract=unknown)
    assert actual is None

    actual = detect_language(title=unknown, abstract=empty)
    assert actual is None

    actual = detect_language(title=unknown, abstract=unknown)
    assert actual is None
