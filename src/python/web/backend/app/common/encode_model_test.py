import pytest  # type: ignore
import web.backend.app.common.encode_model as encode_model
from cryptography.fernet import InvalidToken
from pydantic import BaseModel


class TestModel(BaseModel):
    value1: str
    value2: int


TEST_KEY = encode_model.generate_key()
TEST_MODEL = TestModel(value1="test", value2=1)


def test_encode_and_decode_model() -> None:
    encoded = encode_model.encode(key=TEST_KEY, data=TEST_MODEL)
    decoded = encode_model.decode(key=TEST_KEY, encoded=encoded, model=TestModel)
    assert decoded == TEST_MODEL


def test_encode_and_decode_model_raises_error_with_wrong_key() -> None:
    other_key = encode_model.generate_key()
    encoded = encode_model.encode(key=TEST_KEY, data=TEST_MODEL)
    with pytest.raises(InvalidToken):
        encode_model.decode(key=other_key, encoded=encoded, model=TestModel)
