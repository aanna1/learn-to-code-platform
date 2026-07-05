from abc import ABC, abstractmethod
from typing import Protocol


class Storage(ABC):
    @abstractmethod
    def read(self, key: str) -> bytes:
        ...

    @abstractmethod
    def write(self, key: str, value: bytes) -> None:
        ...

    def exists(self, key: str) -> bool:
        # TODO: call self.read(key) and return True on success, False on KeyError
        pass


class MemoryStorage(Storage):
    def __init__(self) -> None:
        self._data: dict[str, bytes] = {}

    def read(self, key: str) -> bytes:
        # TODO: return stored value, raise KeyError if missing
        pass

    def write(self, key: str, value: bytes) -> None:
        # TODO: store value under key
        pass


class Serializable(Protocol):
    def to_bytes(self) -> bytes: ...


def save_all(items: list, store: Storage) -> None:
    # TODO: for each item, call item.to_bytes() and write to store as "item_0", "item_1", ...
    pass


class Message:
    def __init__(self, text: str) -> None:
        self.text = text

    def to_bytes(self) -> bytes:
        # TODO: return self.text encoded as bytes
        pass


if __name__ == "__main__":
    s = MemoryStorage()
    s.write("hello", b"world")
    print(s.read("hello"))      # b'world'
    print(s.exists("hello"))    # True
    print(s.exists("missing"))  # False

    msgs = [Message("hello"), Message("world")]
    save_all(msgs, s)
    print(s.read("item_0"))     # b'hello'
    print(s.read("item_1"))     # b'world'
