import re
import string

from common.text_cleaning.mixins import TextCleaningMixins
from pylatexenc.latex2text import LatexNodes2Text

SPECIAL_TOKEN_PERCENT = "___pct___"


class BaseTextCleaner(TextCleaningMixins):
    def clean_text(self, text: str) -> str:
        """
        Returns text stripped of all invalid characters with common formatting applied.
        """

        # Standardize common abbrebevations and removes periods
        text = self._multiple_replace(text, self.abbreviations_dict)

        # Remove repetetive punctuation
        text = re.sub(f"([{string.punctuation}])\\1+", "\\1", text)

        # Temporarily replace % sign so the latex function doesn't cut off the sentences
        text = re.sub("%", SPECIAL_TOKEN_PERCENT, text)

        # Standardize people titles (eg. Mr, Mrs, Dr) and removes periods
        text = self._multiple_replace(text, self.titles_dict)

        # Replace latex code with text equivalent
        text = LatexNodes2Text().latex_to_text(text)

        # Replace newlines and tabs with a single character of whitespace
        text = text.replace("\n", " ").replace("\t", " ").replace("\\", "")

        # Clean HTML tags
        text = re.sub(r"<.*?>", "", text)
        text = text.replace("ـ", "")

        # Fix spaces around punctuation
        text = self._fix_spaces(text)

        # Replace currency symbols with their text equivalent
        text = self._multiple_replace(text, self.currencies_dict)

        # Standardize single and double quote variants to a single character
        text = self.single_quote_compile.sub("'", text)
        text = self.double_quote_compile.sub('"', text)

        # Finally ,replace temporarily character with % sign
        text = re.sub(SPECIAL_TOKEN_PERCENT, "%", text)

        return text

    def _multiple_replace(self, text: str, replace_keys_with_values: dict[str, str]) -> str:
        """
        Replaces multiple characters in input text with dictionary mapping.
        """
        pattern = "|".join(map(re.escape, replace_keys_with_values.keys()))
        return re.sub(pattern, lambda m: replace_keys_with_values[m.group()], text)

    def _fix_spaces(self, text: str) -> str:
        """
        Fixes spaces around punctuation and special characters (eg. ()[]{}) to
        avoid issues with tokenizing.
        """
        text = " ".join(text.split())
        # Remove space in []
        text = re.sub(r"\[\s*(.*?)\s*\]", r"[\1]", text)
        # Remove spaces in ()
        text = re.sub(r"\(\s*(.*?)\s*\)", r"(\1)", text)
        # Add space after period, except if it is a decimal point
        text = re.sub(
            r"""((?<=[A-Za-z0-9])\.(?=[A-Za-z]{2})|(?<=[A-Za-z]{2})\.(?=[A-Za-z0-9]))""",
            ". ",
            text,
        )
        text = re.sub(
            r"""((?<=[A-Za-z0-9])\,(?=[A-Za-z]{2})|(?<=[A-Za-z]{2})\,(?=[A-Za-z0-9]))""",
            ", ",
            text,
        )
        # Add space after semicolons(;) colons(:) exclamation points(!) question marks(?)
        text = re.sub(r"(?<=[:;!?])(?=[^\s])", r" ", text)
        # Strip space before punctuation but not after
        text = re.sub(r'\s([?.!"](?:\s|$))', r"\1", text)
        return text
