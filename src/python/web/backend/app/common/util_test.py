import web.backend.app.common.util as util
from pydantic import BaseModel


def test_partition() -> None:
    data = [10, 1, 20, 5]
    below_10, above_10 = util.partition(lambda x: x < 10, data)
    assert below_10 == [1, 5]
    assert above_10 == [10, 20]

    below_30, above_30 = util.partition(lambda x: x < 30, data)
    assert below_30 == [10, 1, 20, 5]
    assert above_30 == []


class TestSelectionFilterInPydanticModel(BaseModel):
    ids: dict[int, bool]


def test_unique_list() -> None:
    data = [10, 1, 20, 5, 1, 3, 10, 300]
    unique_nums, deduped_nums = util.dedup_by_first_unique(lambda x: x, data)
    assert unique_nums == [10, 1, 20, 5, 3, 300]
    assert deduped_nums == [1, 10]

    unique_num_digits, deduped_num_digits = util.dedup_by_first_unique(
        lambda x: str(len(str(x))), data
    )
    assert unique_num_digits == [10, 1, 300]
    assert deduped_num_digits == [20, 5, 1, 3, 10]

    filter_map = {1: True, 10: True}
    unique_nums, deduped_nums = util.dedup_by_first_unique(lambda x: x, data, filter_map)
    assert unique_nums == [20, 5, 3, 300]
    assert deduped_nums == [10, 1, 1, 10]
    assert filter_map == {1: True, 10: True, 20: True, 5: True, 3: True, 300: True}

    filter_model = TestSelectionFilterInPydanticModel(ids={1: True, 10: True, 200: True})
    unique_nums, deduped_nums = util.dedup_by_first_unique(lambda x: x, data, filter_model.ids)
    assert unique_nums == [20, 5, 3, 300]
    assert deduped_nums == [10, 1, 1, 10]
    assert filter_model.ids == {
        1: True,
        10: True,
        20: True,
        5: True,
        3: True,
        300: True,
        200: True,
    }


def test_rounded_percent() -> None:
    assert util.rounded_percent(0) == 0
    assert util.rounded_percent(0.3333333) == 33
    assert util.rounded_percent(0.5) == 50
    assert util.rounded_percent(0.7777777) == 78
    assert util.rounded_percent(0.998) == 100
    assert util.rounded_percent(1.0) == 100


def test_percent_true() -> None:
    data = [2, 4, 5, 7, 10, 13]
    assert util.percent_true(data, lambda x: x % 2 == 0) == 3 / 6
    assert util.percent_true(data, lambda x: x < 10) == 4 / 6
    assert util.percent_true(data, lambda x: x >= 10) == 2 / 6
    assert util.percent_true(data, lambda x: x > 20) == 0 / 6
    assert util.percent_true([], lambda x: x > 20) == 0
