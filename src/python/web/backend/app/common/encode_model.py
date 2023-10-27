import json
from typing import Type, TypeVar

from cryptography.fernet import Fernet
from pydantic import BaseModel

_STR_ENCODING = "utf-8"
_Model = TypeVar("_Model", bound=BaseModel)


def generate_key() -> str:
    """Generates a key to use with encode and decode."""
    return Fernet.generate_key().decode(_STR_ENCODING)


def encode(key: str, data: BaseModel) -> str:
    """Converts a pydantic model to string encoded by the given key."""
    cipher_suite = Fernet(bytes(key, _STR_ENCODING))
    serialized_model = bytes(json.dumps(data.dict()), _STR_ENCODING)
    return cipher_suite.encrypt(serialized_model).decode(_STR_ENCODING)


def decode(key: str, encoded: str, model: Type[_Model]) -> _Model:
    """Converts an key encoded string back into a pydantic model."""
    cipher_suite = Fernet(bytes(key, _STR_ENCODING))
    decoded_text = cipher_suite.decrypt(bytes(encoded, _STR_ENCODING))
    return model(**json.loads(decoded_text))
