from __future__ import annotations
from dataclasses import dataclass, field
import struct
from clocks.misc import bytes_are_same
from typing import Any
from uuid import uuid1


@dataclass
class ScalarClock:
    uuid: bytes = field(default_factory=lambda: uuid1().bytes)
    scalar: int = field(default=0)

    @classmethod
    def setup(cls, options: dict = {}) -> ScalarClock:
        """Set up a new instance."""
        uuid = options['uuid'] if 'uuid' in options else uuid1().bytes
        scalar = options['scalar'] if 'scalar' in options else 0
        return cls(uuid, scalar)

    def advance(self, data: tuple = None) -> tuple[int, bytes]:
        """Create an update that advances the clock to the given time."""
        if data is not None:
            assert type(data) is tuple, 'data must be tuple[int] or None'
            assert type(data[0]) is int, 'data must be tuple[int]'
            return (self.uuid, self.scalar + data[0])

        return (self.uuid, self.scalar + 1)

    def read(self) -> tuple[bytes, int]:
        """Read the current state of the clock."""
        return (self.uuid, self.scalar)

    def update(self, state: tuple) -> ScalarClock:
        """Update the clock if the state verifies."""
        assert type(state) is tuple, 'state must be tuple[bytes, int]'
        assert len(state) == 2, 'state must have len 2'
        assert type(state[0]) is bytes, 'state must be tuple[bytes, int]'
        assert type(state[1]) is int, 'state must be tuple[bytes, int]'

        if not bytes_are_same(state[0], self.uuid):
            return self

        self.scalar = max(self.scalar, state[1]) + 1

        return self

    @staticmethod
    def are_incomparable(ts1: tuple[bytes, int], ts2: tuple[bytes, int]) -> bool:
        """Determine if ts1 and ts2 are incomparable."""
        assert type(ts1) is type(ts2) is tuple, \
            'timestamps must be tuples of form (bytes uuid, int time'
        assert len(ts1) == len(ts2) == 2, \
            'timestamps must be tuples of form (bytes uuid, int time'

        return not bytes_are_same(ts1[0], ts2[0])


    @staticmethod
    def happens_before(ts1: tuple[bytes, int], ts2: tuple[bytes, int]) -> bool:
        """Determine if ts1 happens before ts2."""
        if ScalarClock.are_incomparable(ts1, ts2):
            return False

        return ts1[1] < ts2[1]

    @staticmethod
    def are_concurrent(ts1: tuple[bytes, int], ts2: tuple[bytes, int]) -> bool:
        """Determine if ts1 and ts2 are concurrent."""
        if ScalarClock.are_incomparable(ts1, ts2):
            return False

        return ts1[1] == ts2[1]

    def pack(self) -> bytes:
        """Pack the clock down to bytes."""
        return struct.pack('!16sI', self.uuid, self.scalar)

    @classmethod
    def unpack(cls, data: bytes) -> ScalarClock:
        """Unpack a clock from bytes."""
        assert type(data) is bytes, 'data must be bytes of len 20'
        assert len(data) == 20, 'data must be bytes of len 20'

        return cls(*struct.unpack('!16sI', data))
