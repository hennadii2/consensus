import time
from typing import Optional, Protocol

from loguru import logger


class LogTimingWithOptional(Protocol):
    def __call__(self, normalize_by: Optional[int] = None) -> None:
        ...


def time_endpoint_event(endpoint: str, event: str) -> LogTimingWithOptional:
    """
    Starts a timer and returns a callback thats stops the timer and logs an
    INFO event with the timing info in nanoseconds for the given endpoint and
    event name.
    """
    start = time.perf_counter_ns()

    def stop_timer_and_log(normalize_by: Optional[int] = None) -> None:
        end = time.perf_counter_ns()
        total = end - start

        event_str = event
        if normalize_by:
            total = int(total / normalize_by)
            event_str = f"{event_str}_normalized"

        logger.info(f"Timing log: {endpoint}: {event_str}: {total} ns")

    return stop_timer_and_log
