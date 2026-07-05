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
        try:
            self.read(key)
            return True
        except KeyError:
            return False


class MemoryStorage(Storage):
    def __init__(self) -> None:
        self._data: dict[str, bytes] = {}

    def read(self, key: str) -> bytes:
        return self._data[key]

    def write(self, key: str, value: bytes) -> None:
        self._data[key] = value


class Serializable(Protocol):
    def to_bytes(self) -> bytes: ...


def save_all(items: list, store: Storage) -> None:
    for i, item in enumerate(items):
        store.write(f"item_{i}", item.to_bytes())


class Message:
    def __init__(self, text: str) -> None:
        self.text = text

    def to_bytes(self) -> bytes:
        return self.text.encode()


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
