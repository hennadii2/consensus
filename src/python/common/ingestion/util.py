from typing import Optional

from langdetect import detect  # type: ignore


def detect_language(title: Optional[str], abstract: Optional[str]) -> Optional[str]:
    """Returns a detected language or None if an error occurs"""

    def language_or_none(text: Optional[str]) -> Optional[str]:
        try:
            language = detect(text)
            return str(language)
        except Exception:
            return None

    abstract_language = language_or_none(abstract)
    if abstract_language:
        return abstract_language
    title_language = language_or_none(title)
    if title_language:
        return title_language
    return None
