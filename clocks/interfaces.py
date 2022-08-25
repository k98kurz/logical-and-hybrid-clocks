from __future__ import annotations
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class QueueProtocol(Protocol):
    def __init__(self, size: int = 10, items: list = []) -> None:
        """Initialize with size and items."""
        ...

    def read(self) -> list[Any]:
        """Return the current values."""
        ...

    def get(self) -> Any:
        """Return the first value."""
        ...

    def take(self) -> Any:
        """Remove the first value and return it."""
        ...

    def remove(self, index: int, number: int = 1) -> None:
        """Remove the number of elements in priority order."""
        ...

    def append(self, item: Any) -> None:
        """Append to the list, kicking out oldest if necessary."""
        ...

    def extend(self, items: list[Any]) -> None:
        """Extend the list with items, kicking out oldest elements if necessary."""
        ...


@runtime_checkable
class ClockProtocol(Protocol):
    """Duck typed Protocol showing what a clock must do."""
    @classmethod
    def setup(cls, options: dict = {}) -> ClockProtocol:
        """Set up a new instance."""
        ...

    def advance(self, data: tuple) -> tuple:
        """Create an update that advances the clock to the given time."""
        ...

    def read(self) -> tuple:
        """Read the current state of the clock."""
        ...

    def update(self, state: tuple = None) -> ClockProtocol:
        """Update the clock if the state verifies."""
        ...

    @staticmethod
    def are_incomparable(ts1: Any, ts2: Any) -> bool:
        """Determine if ts1 and ts2 are incomparable."""
        ...

    @staticmethod
    def happens_before(ts1: Any, ts2: Any) -> bool:
        """Determine if ts1 happens before ts2."""
        ...

    @staticmethod
    def are_concurrent(ts1: Any, ts2: Any) -> bool:
        """Determine if ts1 and ts2 are concurrent."""
        ...

    def pack(self) -> bytes:
        """Pack the clock down to bytes."""
        ...

    @classmethod
    def unpack(cls, data: bytes) -> ClockProtocol:
        """Unpack a clock from bytes."""
        ...


@runtime_checkable
class ChainClockProtocol(Protocol):
    """Duck typed Protocol showing what a chain clock must do."""
    ...


@runtime_checkable
class HybridTimeProtocol(Protocol):
    """Duck typed Protocol showing what a HybridTime clock must do."""
    def calculate_offset(timestamps: list[tuple[int, int, int, int]]) -> tuple[int]:
        """Calculate the offset with a neighbor in the cluster. Input
            format is a tuple or list of observations; each observation
            is of form (local_ts_sent, foreign_ts_received,
            foreign_ts_sent, local_ts_received), each ts in seconds
            since Unix epoch as calculated by physical system clocks.
        """
        ...

    def synchronize(time_offsets: tuple[int]) -> HybridTimeProtocol:
        """Synchronize to the median clock of the cluster."""
        ...
