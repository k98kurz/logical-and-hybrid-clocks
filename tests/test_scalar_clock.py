from random import randint
import struct
from context import interfaces, ScalarClock
import unittest


class TestScalarClock(unittest.TestCase):
    """Test suite for classes."""
    def test_imports_without_error(self):
        pass

    def test_ScalarClock_implements_ClockProtocol(self):
        assert issubclass(ScalarClock, interfaces.ClockProtocol), \
            'ScalarClock must implement ClockProtocol'

    def test_ScalarClock_instance_has_int_scalar_an_bytes_uuid_properties(self):
        clock = ScalarClock()
        assert hasattr(clock, 'scalar'), 'ScalarClock instance must have scalar property'
        assert type(clock.scalar) is int, 'clock.scalar must be int'
        assert hasattr(clock, 'uuid'), 'ScalarClock instance must have uuid property'
        assert type(clock.uuid) is bytes, 'clock.uuid must be bytes'

    def test_ScalarClock_instances_have_different_uuids(self):
        assert ScalarClock().uuid != ScalarClock().uuid, \
            'uuids must be different for different ScalarClock instances'

    def test_ScalarClock_setup_returns_instance(self):
        clock = ScalarClock.setup()
        assert isinstance(clock, ScalarClock), 'ScalarClock.setup must return instance'

    def test_ScalarClock_setup_accepts_uuid_and_scalar_fields_in_options(self):
        clock = ScalarClock.setup({'uuid': b'123', 'scalar': 55})
        assert clock.uuid == b'123', 'uuid must match that specified in setup'
        assert clock.scalar == 55, 'scalar must match that specified in setup'

        clock = ScalarClock.setup({'uuid': b'321', 'scalar': 99})
        assert clock.uuid == b'321', 'uuid must match that specified in setup'
        assert clock.scalar == 99, 'scalar must match that specified in setup'

    def test_ScalarClock_advance_returns_update_with_tuple_int_bytes_form(self):
        clock = ScalarClock()
        update = clock.advance()

        assert type(update) is tuple, 'ClockProtocol.advance() must return tuple'
        assert len(update) == 2, 'ScalarClock().advance() must return tuple[bytes, int]'
        assert type(update[0]) is bytes, 'ScalarClock().advance() must return tuple[bytes, int]'
        assert type(update[1]) is int, 'ScalarClock().advance() must return tuple[bytes, int]'
        assert update[0] == clock.uuid, 'ScalarClock().advance()[0] must be uuid'

    def test_ScalarClock_read_returns_tuple_of_bytes_int(self):
        clock = ScalarClock()
        ts = clock.read()
        assert type(ts) is tuple, 'ScalarClock().read() must return tuple[bytes, int]'
        assert len(ts) == 2
        assert type(ts[0]) is bytes
        assert ts[0] == clock.uuid
        assert type(ts[1]) is int

    def test_ScalarClock_advance_on_tuple_int_increases_by_that_value(self):
        clock = ScalarClock()
        assert clock.advance()[1] == 1
        assert clock.advance((5,))[1] == 5

    def test_ScalarClock_update_changes_scalar_state_and_increases_read_output(self):
        clock = ScalarClock()
        advance_to = randint(0, 999)
        clock.update((clock.uuid, advance_to))
        assert clock.scalar == clock.read()[1] == advance_to + 1, \
            f'clock should advance to {advance_to+1}'

        clock.update((clock.uuid, advance_to*2))
        assert clock.scalar == clock.read()[1] == advance_to*2 + 1, \
            f'clock should advance to {advance_to*2+1}'

    def test_ScalarClock_update_unaffected_by_mismatched_uuid(self):
        clock = ScalarClock()
        update = (b'not the uuid', 12)
        ts0 = clock.read()
        clock.update(update)
        ts1 = clock.read()

        assert ts0 == ts1, 'timestamps should be the same'

    def test_ScalarClock_are_incomparable_functions(self):
        clock0, clock1 = ScalarClock(), ScalarClock()
        ts0 = clock0.read()
        ts1 = clock1.read()
        assert type(ScalarClock.are_incomparable(ts0, ts1)) is bool, \
            'ScalarClock.are_incomparable must return bool'
        assert ScalarClock.are_incomparable(ts0, ts1), 'should be True'
        clock0.update(clock0.advance((1,)))
        assert not ScalarClock.are_incomparable(ts0, clock0.read()), 'should be False'

    def test_ScalarClock_happens_before_functions(self):
        clock = ScalarClock()
        ts0 = clock.read()
        ts1 = clock.read()
        assert type(ScalarClock.happens_before(ts0, ts1)) is bool, \
            'happens_before() must return bool'
        assert not ScalarClock.happens_before(ts0, ts1), \
            'happens_before() should return False for concurrent timestamps'
        clock.update(clock.advance((1,)))
        ts2 = clock.read()
        assert ScalarClock.happens_before(ts0, ts2), \
            'happens_before(ts1, ts2) should return True for ts1<ts2'
        assert not ScalarClock.happens_before(ScalarClock().read(), ts2), \
            'happens_before() should return False for incomparable timestamps'

    def test_ScalarClock_are_concurrent_functions(self):
        clock = ScalarClock()
        ts0 = clock.read()
        ts1 = clock.read()
        assert type(ScalarClock.are_concurrent(ts0, ts1)) is bool, \
            'are_concurrent() must return bool'
        assert ScalarClock.are_concurrent(ts0, ts1), \
            'are_concurrent(ts1, ts2) should return True for ts1 == ts2'
        clock.update(clock.advance((1,)))
        ts2 = clock.read()
        assert not ScalarClock.are_concurrent(ts0, ts2), \
            'are_concurrent(ts1, ts2) should return False for ts1 != ts2'
        assert not ScalarClock.are_concurrent(ScalarClock().read(), ts2), \
            'are_concurrent() should return False for incomparable timestamps'

    def test_ScalarClock_pack_returns_bytes_of_form_uuid_int(self):
        clock = ScalarClock()
        packed = clock.pack()
        assert type(packed) is bytes, 'pack() must return bytes'
        assert len(packed) == len(clock.uuid) + 4, \
            f'pack() len must be {len(clock.uuid) + 4}'
        assert packed == struct.pack(f'!{len(clock.uuid)}sI', clock.uuid, clock.scalar), \
            'pack() output should return uuid and scalar packed with struct'

    def test_ScalarClock_unpack_returns_ScalarClock_instance(self):
        clock = ScalarClock()
        packed = struct.pack(f'!{len(clock.uuid)}sI', clock.uuid, clock.scalar)
        unpacked = ScalarClock.unpack(packed)
        assert isinstance(unpacked, ScalarClock), \
            'unpack() must return ScalarClock instance'
        assert unpacked.uuid == clock.uuid, 'uuid must match'
        assert unpacked.scalar == clock.scalar, 'scalar must match'


if __name__ == '__main__':
    unittest.main()
