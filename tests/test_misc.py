from random import randint
from context import interfaces, misc
import unittest


class TestMapClock(unittest.TestCase):
    """Test suite for classes."""
    def test_imports_without_error(self):
        pass

    # helper function tests
    def test_xor_returns_bytes_with_correct_values(self):
        assert type(misc.xor(b'123', b'321')) is bytes
        assert misc.xor(b'123', b'321') == b'\x02\x00\x02'
        assert misc.xor(b'yellow s', b'ubmarine') == b'\x0c\x07\x01\r\x1d\x1eN\x16'

    def test_bytes_are_same_returns_bool(self):
        assert type(misc.bytes_are_same(b'123', b'121')) is bool
        assert not misc.bytes_are_same(b'123', b'121')
        assert not misc.bytes_are_same(b'123', b'12')
        assert misc.bytes_are_same(b'123', b'123')

    def test_all_ascii_returns_bool(self):
        assert type(misc.all_ascii(b'1234')) is bool
        assert misc.all_ascii(b'1234')
        assert not misc.all_ascii(b'1234\x01')

    def test_hexify_returns_input_type_except_for_non_ascii_bytes(self):
        assert type(misc.hexify(b'123')) is bytes
        assert type(misc.hexify('123')) is str
        assert type(misc.hexify([1,2,3])) is list
        assert type(misc.hexify((1,2,3))) is tuple
        assert type(misc.hexify(1)) is int
        assert misc.hexify(None) is None
        assert type(misc.hexify({'str1': 'str2'})) is dict
        assert type(misc.hexify(b'\x03')) is str

    def test_hexify_is_recursive(self):
        testvector = {
            b'\x01\x02': [1,2],
            'str key': {
                'str key': b'bytes val'
            }
        }
        hexed = misc.hexify(testvector)
        assert type(hexed) is dict
        assert '0102' in hexed
        assert type(hexed['0102']) is list
        assert hexed['str key']['str key'] == b'bytes val'

    # BoundedQueue tests
    def test_BoundedQueue_implements_QueueProtocol(self):
        assert issubclass(misc.BoundedQueue, interfaces.QueueProtocol)

    def test_BoundedQueue_initializes_with_size_and_items(self):
        bq = misc.BoundedQueue()
        assert hasattr(bq, 'size'), 'BoundedQueue must initialize with int size'
        assert hasattr(bq, 'items'), 'BoundedQueue must initialize with list items'
        assert type(bq.size) is int, 'BoundedQueue must initialize with int size'
        assert type(bq.items) is list, 'BoundedQueue must initialize with list items'

        bq = misc.BoundedQueue(size=2, items=[1,2])
        assert bq.size == 2
        assert bq.items == [1,2]

    def test_BoundedQueue_read_returns_items(self):
        bq = misc.BoundedQueue(size=3, items=[1,2,3])
        assert bq.read() == [*bq.items]

    def test_BoundedQueue_get_returns_zeroeth_item(self):
        bq = misc.BoundedQueue(size=3, items=[1,2,3])
        assert bq.get() == bq.items[0]

    def test_BoundedQueue_take_removes_and_returns_zeroeth_item(self):
        bq = misc.BoundedQueue(size=3, items=[1,2,3])
        assert bq.take() == 1
        assert bq.items == [2,3]

    def test_BoundedQueue_remove_removes_items(self):
        bq = misc.BoundedQueue(size=3, items=[1,2,3])
        bq.remove(0, 2)
        assert bq.read() == [3]
        bq = misc.BoundedQueue(size=3, items=[1,2,3])
        bq.remove(1, 1)
        assert bq.read() == [1,3]

    def test_BoundedQueue_append_appends_item(self):
        bq = misc.BoundedQueue(size=3, items=[1,2])
        bq.append(3)
        assert bq.read()[-1] == 3

    def test_BoundedQueue_append_removes_lower_index_items(self):
        bq = misc.BoundedQueue(size=3, items=[1,2,3])
        bq.append(4)
        assert bq.read() == [2,3,4]
        bq.append(5)
        assert bq.read() == [3,4,5]

    def test_BoundedQueue_extend_extends_items(self):
        bq = misc.BoundedQueue(size=3, items=[1])
        bq.extend([2,3])
        assert bq.read() == [1,2,3]

    def test_BoundedQueue_extend_removes_lower_index_items(self):
        bq = misc.BoundedQueue(size=3, items=[1,2,3])
        bq.extend([4,5])
        assert bq.read() == [3,4,5]
        bq.extend([6,7])
        assert bq.read() == [5,6,7]


if __name__ == '__main__':
    unittest.main()
