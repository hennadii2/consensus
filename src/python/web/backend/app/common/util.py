from typing import Callable, Iterable, Optional, TypeVar

_DataType = TypeVar("_DataType")
_SelectType = TypeVar("_SelectType")


def partition(
    pred: Callable[[_DataType], bool], iterable: Iterable[_DataType]
) -> tuple[list[_DataType], list[_DataType]]:
    """Splits an interable into two lists based on passing or failing a condition."""
    trues: list[_DataType] = []
    falses: list[_DataType] = []
    for item in iterable:
        if pred(item):
            trues.append(item)
        else:
            falses.append(item)
    return trues, falses


def dedup_by_first_unique(
    selector: Callable[[_DataType], _SelectType],
    items: Iterable[_DataType],
    filter_map: Optional[dict[_SelectType, bool]] = None,
) -> tuple[list[_DataType], list[_DataType]]:
    """
    Returns the unique list of items and deduped items based on a custom selector.
    Like calling set() with a custom selector.

    If filter_map is provided, it is passed by ref, and the dict will be modified
    in place with newly seen values.
    """
    seen_values: dict[_SelectType, bool] = {} if filter_map is None else filter_map
    unique_items: list[_DataType] = []
    deduped_items: list[_DataType] = []
    for item in items:
        value = selector(item)
        if value in seen_values:
            deduped_items.append(item)
        else:
            unique_items.append(item)
            seen_values[value] = True
    return unique_items, deduped_items


def rounded_percent(value: float) -> int:
    """Returns a number rounded to its nearset integer percent."""
    return round(value * 100)


def percent_true(iterable: Iterable[_DataType], pred: Callable[[_DataType], bool]) -> float:
    """Percentage of results where the predicate is true."""
    total_count = len(list(iterable))
    if total_count == 0:
        return 0

    count = sum(map(pred, iterable))
    return count / total_count
