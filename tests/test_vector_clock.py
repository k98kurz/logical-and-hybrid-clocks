from random import randint
import struct
from context import interfaces, VectorClock
import unittest


class TestVectorClock(unittest.TestCase):
    """Test suite for classes."""
    def test_imports_without_error(self):
        pass

    def test_VectorClock_implements_ClockProtocol(self):
        assert issubclass(VectorClock, interfaces.ClockProtocol), \
            'VectorClock must implement ClockProtocol'

    def test_VectorClock_instance_has_bytes_uuid_tuple_vector_and_index_properties(self):
        clock = VectorClock()
        assert hasattr(clock, 'uuid'), 'VectorClock instance must have uuid property'
        assert type(clock.uuid) is bytes, 'clock.uuid must be bytes'
        assert hasattr(clock, 'vector'), 'VectorClock instance must have vector property'
        assert type(clock.vector) is tuple, 'clock.vector must be tuple'
        assert hasattr(clock, 'index'), 'VectorClock instance must have index property'
        assert type(clock.index) is int, 'clock.index must be int'

    def test_VectorClock_instances_have_different_uuids(self):
        assert VectorClock().uuid != VectorClock().uuid, \
            'uuids must be different for different VectorClock instances'

    def test_VectorClock_setup_returns_instance(self):
        clock = VectorClock.setup()
        assert isinstance(clock, VectorClock), 'VectorClock.setup must return instance'

    def test_VectorClock_setup_accepts_uuid_and_Vector_fields_in_options(self):
        clock = VectorClock.setup({'uuid': b'123', 'vector': (55,)})
        assert clock.uuid == b'123', 'uuid must match that specified in setup'
        assert clock.vector == (55,), 'vector must match that specified in setup'

        clock = VectorClock.setup({'uuid': b'321', 'vector': (99,)})
        assert clock.uuid == b'321', 'uuid must match that specified in setup'
        assert clock.vector == (99,), 'vector must match that specified in setup'

    def test_VectorClock_advance_returns_update_with_tuple_bytes_tuple_int_form(self):
        clock = VectorClock()
        update = clock.advance()

        assert type(update) is tuple, 'ClockProtocol.advance() must return tuple'
        assert len(update) == 2, \
            'VectorClock().advance() must return tuple[bytes, tuple[int]]'
        assert type(update[0]) is bytes, \
            'VectorClock().advance() must return tuple[bytes, tuple[int]]'
        assert type(update[1]) is tuple, \
            'VectorClock().advance() must return tuple[bytes, tuple[int]]'
        assert type(update[1][0]) is int, \
            'VectorClock().advance() must return tuple[bytes, tuple[int]]'
        assert update[0] == clock.uuid, 'VectorClock().advance()[0] must be uuid'
        assert update[1][0] == clock.vector[clock.index] + 1

    def test_VectorClock_read_returns_tuple_of_bytes_tuple_int(self):
        clock = VectorClock()
        ts = clock.read()
        assert type(ts) is tuple, \
            'VectorClock().read() must return tuple[bytes, tuple[int]]'
        assert len(ts) == 2
        assert type(ts[0]) is bytes
        assert ts[0] == clock.uuid
        assert type(ts[1]) is tuple
        assert type(ts[1][0]) is int

    def test_VectorClock_advance_on_tuple_int_increases_correct_index_by_that_value(self):
        clock = VectorClock(vector=(0,0), index=1)
        assert clock.advance()[1][0] == 0
        assert clock.advance((5,))[1][1] == 5

    def test_VectorClock_update_changes_Vector_state_and_increases_read_output(self):
        clock = VectorClock()
        advance_to = randint(0, 999)
        clock.update((clock.uuid, (advance_to,)))
        assert clock.vector[0] == clock.read()[1][0] == advance_to + 1, \
            f'clock should update to {advance_to+1}'

        clock.update((clock.uuid, (advance_to*2,)))
        assert clock.vector[0] == clock.read()[1][0] == advance_to*2 + 1, \
            f'clock should update to {advance_to*2+1}'

    def test_VectorClock_update_unaffected_by_mismatched_uuid(self):
        clock = VectorClock()
        update = (b'not the uuid', (12,))
        ts0 = clock.read()
        clock.update(update)
        ts1 = clock.read()

        assert ts0 == ts1, 'timestamps should be the same'

    def test_VectorClock_are_incomparable_functions(self):
        clock0, clock1 = VectorClock(), VectorClock()
        ts0 = clock0.read()
        ts1 = clock1.read()
        assert type(VectorClock.are_incomparable(ts0, ts1)) is bool, \
            'VectorClock.are_incomparable must return bool'
        assert VectorClock.are_incomparable(ts0, ts1), 'should be True'
        clock0.update(clock0.advance((1,)))
        assert not VectorClock.are_incomparable(ts0, clock0.read()), 'should be False'

    def test_VectorClock_happens_before_functions(self):
        clock = VectorClock()
        ts0 = clock.read()
        ts1 = clock.read()
        assert type(VectorClock.happens_before(ts0, ts1)) is bool, \
            'happens_before() must return bool'
        assert not VectorClock.happens_before(ts0, ts1), \
            'happens_before() should return False for concurrent timestamps'
        clock.update(clock.advance((1,)))
        ts2 = clock.read()
        assert VectorClock.happens_before(ts0, ts2), \
            'happens_before(ts1, ts2) should return True for ts1<=ts2'
        assert not VectorClock.happens_before(VectorClock().read(), ts2), \
            'happens_before() should return False for incomparable timestamps'

    def test_VectorClock_are_concurrent_functions(self):
        clock = VectorClock(vector=(0,0))
        clock2 = VectorClock(uuid=clock.uuid, vector=clock.vector, index=1)
        ts0 = clock.read()
        ts1 = clock.read()
        assert type(VectorClock.are_concurrent(ts0, ts1)) is bool, \
            'are_concurrent() must return bool'
        assert VectorClock.are_concurrent(ts0, ts1), \
            'are_concurrent(ts1, ts2) should return True for neither happens_before'
        clock.update(clock.advance((1,)))
        clock2.update(clock2.advance((1,)))
        ts1 = clock.read()
        ts2 = clock2.read()
        assert not VectorClock.are_concurrent(ts0, ts2), \
            'are_concurrent(ts1, ts2) should return False for happens_before(ts1, ts2)' + \
            ' or happens_before(ts2, ts1)'
        assert not VectorClock.are_concurrent(VectorClock().read(), ts2), \
            'are_concurrent() should return False for incomparable timestamps'
        assert VectorClock.are_concurrent(ts1, ts2), \
            'are_concurrent(ts1, ts2) should return True for neither happens_before'

    def test_VectorClock_pack_returns_bytes_of_form_uuid_int_ints(self):
        clock = VectorClock()
        packed = clock.pack()
        assert type(packed) is bytes, 'pack() must return bytes'
        assert len(packed) == 24, 'pack() len must be 24'
        assert packed == struct.pack(
            f'!16sI{"".join(["I" for _ in clock.vector])}',
            clock.uuid,
            clock.index,
            *clock.vector
        ), 'pack() output should return uuid and vector packed with struct'

    def test_VectorClock_unpack_returns_VectorClock_instance(self):
        clock = VectorClock.setup({'vector': (1, 2, 3)})
        packed = struct.pack(
            f'!16sI{"".join(["I" for _ in clock.vector])}',
            clock.uuid,
            clock.index,
            *clock.vector
        )
        unpacked = VectorClock.unpack(packed)
        assert isinstance(unpacked, VectorClock), \
            'unpack() must return VectorClock instance'
        assert unpacked.uuid == clock.uuid, 'uuid must match'
        assert unpacked.vector == clock.vector, 'vector must match'
        assert unpacked.index == clock.index, 'index must match'


if __name__ == '__main__':
    unittest.main()
