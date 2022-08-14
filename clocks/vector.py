from __future__ import annotations
import struct
from clocks.misc import bytes_are_same
from dataclasses import dataclass, field
from uuid import uuid1


@dataclass
class VectorClock:
    uuid: bytes = field(default_factory=lambda: uuid1().bytes)
    index: int = field(default=0)
    vector: tuple = field(default=(0,))

    @classmethod
    def setup(cls, options: dict = {}) -> VectorClock:
        """Set up a new instance."""
        assert type(options) is dict, 'options must be dict'

        uuid = options['uuid'] if 'uuid' in options else uuid1().bytes
        vector = options['vector'] if 'vector' in options else (0,)
        index = options['index'] if 'index' in options else 0

        return cls(uuid, index, vector)

    def advance(self, data: tuple = None) -> tuple[bytes, tuple[int]]:
        """Create an update that advances the clock to the given time."""
        if data is not None:
            assert type(data) is tuple, 'data must be tuple[int] or None'
            assert type(data[0]) is int, 'data must be tuple[int]'

        vector = [*self.vector]
        vector[self.index] += data[0] if data is not None else 1
        return (self.uuid, (*vector,))

    def read(self) -> tuple:
        """Read the current state of the clock."""
        return (self.uuid, (*self.vector,))

    def update(self, state: tuple = None) -> VectorClock:
        """Update the clock if the state verifies."""
        if state is None:
            return self

        assert type(state) is tuple, 'state must be tuple[bytes, tuple[int]]'
        assert type(state[0]) is bytes, 'state must be tuple[bytes, tuple[int]]'
        assert type(state[1]) is tuple, 'state must be tuple[bytes, tuple[int]]'
        assert len(state[1]) == len(self.vector), 'state[1] len must match vector'
        for s in state[1]:
            assert type(s) is int, 'state must be tuple[bytes, tuple[int]]'

        if not bytes_are_same(state[0], self.uuid):
            return self

        vector = [*self.vector]
        for i, v in enumerate(state[1]):
            vector[i] = max(vector[i], v)

        vector[self.index] += 1

        self.vector = (*vector,)

        return self

    @staticmethod
    def are_incomparable(ts1: tuple[bytes, tuple[int]], ts2: tuple[bytes, tuple[int]]) -> bool:
        """Determine if ts1 and ts2 are incomparable."""
        assert type(ts1) is type(ts2) is tuple, \
            'ts1 and ts2 must be tuple[bytes, tuple[int]]'
        assert type(ts1[0]) is type(ts2[0]) is bytes, \
            'ts1 and ts2 must be tuple[bytes, tuple[int]]'
        assert type(ts1[1]) is type(ts2[1]) is tuple, \
            'ts1 and ts2 must be tuple[bytes, tuple[int]]'

        return len(ts1[1]) != len(ts2[1]) or not bytes_are_same(ts1[0], ts2[0])

    @staticmethod
    def happens_before(ts1: tuple[bytes, tuple[int]], ts2: tuple[bytes, tuple[int]]) -> bool:
        """Determine if ts1 happens before ts2."""
        if VectorClock.are_incomparable(ts1, ts2):
            return False

        at_least_one_before = False
        at_least_one_after = False

        for i, _ in enumerate(ts1[1]):
            assert type(ts1[1][i]) is type(ts2[1][i]) is int, \
                'ts1 and ts2 must be tuple[bytes, tuple[int]]'

            if ts1[1][i] < ts2[1][i]:
                at_least_one_before = True

            if ts1[1][i] > ts2[1][i]:
                at_least_one_after = True

        return at_least_one_before and not at_least_one_after

    @staticmethod
    def are_concurrent(ts1: tuple[bytes, tuple[int]], ts2: tuple[bytes, tuple[int]]) -> bool:
        """Determine if ts1 and ts2 are concurrent."""
        if VectorClock.are_incomparable(ts1, ts2):
            return False

        return not VectorClock.happens_before(ts1, ts2) and not \
            VectorClock.happens_before(ts2, ts1)

    def pack(self) -> bytes:
        """Pack the clock down to bytes."""
        return struct.pack(
            '!16sI' + ''.join(['I' for i in self.vector]),
            self.uuid,
            self.index,
            *self.vector
        )

    @classmethod
    def unpack(cls, data: bytes) -> VectorClock:
        """Unpack a clock from bytes."""
        assert type(data) is bytes, 'data must be bytes of len >= 24'
        assert len(data) >= 24, 'data must be bytes of len >= 24'
        assert len(data) % 4 == 0, 'data must be bytes of len % 4 = 0'

        vector_size = (len(data) - 20) // 4

        uuid, index = struct.unpack(
            '!16sI',
            data[:20]
        )
        vector = struct.unpack(
            '!' + ''.join(['I' for _ in range(vector_size)]),
            data[20:]
        )

        return cls(uuid, index, vector)


class MapClock:
    ...
