from dataclasses import dataclass, field
from typing import Any, Optional


# helper functions
def xor(b1: bytes, b2: bytes) -> bytes:
    """XOR two equal-length byte strings together."""
    b3 = bytearray()
    for i in range(len(b1)):
        b3.append(b1[i] ^ b2[i])

    return bytes(b3)

def bytes_are_same(b1: bytes, b2: bytes) -> bool:
    """Timing-attack safe bytes comparison."""
    return len(b1) == len(b2) and int.from_bytes(xor(b1, b2), 'little') == 0

def all_ascii(data: bytes) -> bool:
    """Determine if all bytes are displayable ascii chars."""
    for c in data:
        if c < 32 or c > 126:
            return False

    return True

def hexify(data) -> Any:
    """Convert bytes to hex."""

    if type(data) is bytes and not all_ascii(data):
        return data.hex()

    if type(data) in (tuple, list):
        result = []
        for v in data:
            result.append(hexify(v))

        return result if type(data) is list else tuple(result)

    if type(data) is dict:
        result = {}

        for key in data:
            name = hexify(key)
            result[name] = hexify(data[key])

        return result

    return data


# queue
@dataclass
class BoundedQueue:
    size: int = field(default=10)
    items: list = field(default_factory=list)

    def read(self) -> list[Any]:
        """Return the current values."""
        return [*self.items]

    def get(self) -> Optional[Any]:
        """Return the first value."""
        return self.items[0] if len(self.items) > 0 else None

    def take(self) -> Any:
        """Remove the first value and return it."""
        if len(self.items) == 0:
            return None
        result, self.items = self.items[0], self.items[1:]
        return result

    def remove(self, index: int, number: int = 1) -> None:
        """Remove the number of elements in priority order."""
        assert type(index) is int, 'index must be int'
        assert type(number) is int, 'number must be int'
        assert len(self.items) > index + number, 'not enough items in queue'

        self.items = [*self.items[:index], *self.items[index+number:]]

    def append(self, item: Any) -> None:
        """Append to the list, kicking out oldest if necessary."""
        self.items.append(item)

        if len(self.items) > self.size:
            self.items = self.items[-self.size:]

    def extend(self, items: list[Any]) -> None:
        """Extend the list with items, kicking out oldest elements if necessary."""
        assert type(items) in (list, tuple), 'items must be list or tuple'
        self.items.extend(items)

        if len(self.items) > self.size:
            self.items = self.items[-self.size:]
