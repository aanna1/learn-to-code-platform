from submission import Storage, MemoryStorage, Serializable, save_all, Message


def test_storage_is_abstract():
    """Storage cannot be instantiated directly."""
    try:
        Storage()
        assert False, "Storage() should raise TypeError for missing abstract methods"
    except TypeError:
        pass


def test_memory_storage_write_and_read():
    """MemoryStorage stores and retrieves bytes by key."""
    s = MemoryStorage()
    s.write("key", b"value")
    result = s.read("key")
    assert result == b"value", (
        f"read('key') should return b'value' after write('key', b'value'), got {result!r}. "
        "Store the value in self._data and return self._data[key] in read()."
    )


def test_memory_storage_read_missing_raises_key_error():
    """MemoryStorage.read raises KeyError for missing keys."""
    s = MemoryStorage()
    try:
        s.read("missing")
        assert False, "read('missing') should raise KeyError"
    except KeyError:
        pass


def test_storage_exists_true():
    """exists() returns True when the key is present."""
    s = MemoryStorage()
    s.write("x", b"1")
    result = s.exists("x")
    assert result is True, (
        f"exists('x') should return True after writing 'x', got {result!r}. "
        "Call self.read(key) inside a try/except KeyError."
    )


def test_storage_exists_false():
    """exists() returns False when the key is absent."""
    s = MemoryStorage()
    result = s.exists("nope")
    assert result is False, (
        f"exists('nope') should return False when the key was never written, got {result!r}."
    )


def test_storage_exists_inherited():
    """exists() is inherited from Storage, not redefined on MemoryStorage."""
    import inspect
    assert "exists" not in MemoryStorage.__dict__, (
        "exists() should live on Storage, not MemoryStorage. "
        "Remove it from MemoryStorage and let subclasses inherit it for free."
    )


def test_message_to_bytes():
    """Message.to_bytes() encodes self.text."""
    m = Message("hello")
    result = m.to_bytes()
    assert result == b"hello", (
        f"Message('hello').to_bytes() should return b'hello', got {result!r}. "
        "Return self.text.encode()."
    )


def test_save_all_writes_items():
    """save_all writes each item as item_0, item_1, etc."""
    s = MemoryStorage()
    msgs = [Message("hello"), Message("world")]
    save_all(msgs, s)
    assert s.read("item_0") == b"hello", (
        f"After save_all, item_0 should be b'hello', got {s.read('item_0')!r}. "
        "Use f'item_{{i}}' as the key for each item."
    )
    assert s.read("item_1") == b"world", (
        f"After save_all, item_1 should be b'world', got {s.read('item_1')!r}."
    )


def test_save_all_three_items():
    """save_all handles any number of items."""
    s = MemoryStorage()
    save_all([Message("a"), Message("b"), Message("c")], s)
    assert s.read("item_2") == b"c", (
        f"item_2 should be b'c', got {s.read('item_2')!r}."
    )


def test_message_no_storage_inheritance():
    """Message does not inherit from Storage (it satisfies Serializable structurally)."""
    assert not issubclass(Message, Storage), (
        "Message should not inherit from Storage. "
        "It satisfies the Serializable Protocol structurally by having to_bytes()."
    )


if __name__ == "__main__":
    s = MemoryStorage()
    s.write("hello", b"world")
    print("read:", s.read("hello"))
    print("exists:", s.exists("hello"))
    save_all([Message("hello"), Message("world")], s)
    print("item_0:", s.read("item_0"))
