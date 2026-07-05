from submission import Record, UpperMixin, PrefixMixin, ProcessedRecord, get_mro_names


def test_record_process_basic():
    """Record.process returns ['Record:<name>']."""
    r = Record(name="alice")
    result = r.process()
    assert result == ["Record:alice"], (
        f"Record(name='alice').process() should return ['Record:alice'], got {result}. "
        "Return [f'Record:{self.name}']."
    )


def test_upper_mixin_uppercases():
    """UpperMixin.process uppercases every string from super().process()."""
    class Base:
        def process(self):
            return ["hello", "world"]
    class Up(UpperMixin, Base):
        pass
    result = Up().process()
    assert result == ["HELLO", "WORLD"], (
        f"UpperMixin should uppercase every string from super().process(), got {result}. "
        "Use [s.upper() for s in super().process()]."
    )


def test_prefix_mixin_prepends():
    """PrefixMixin.process prepends 'prefix:' to every string from super().process()."""
    class Base:
        def process(self):
            return ["foo", "bar"]
    class Pre(PrefixMixin, Base):
        pass
    result = Pre(prefix="X").process()
    assert result == ["X:foo", "X:bar"], (
        f"PrefixMixin(prefix='X').process() should give ['X:foo', 'X:bar'], got {result}. "
        "Use [f'{self.prefix}:{s}' for s in super().process()]."
    )


def test_processed_record_full_chain():
    """ProcessedRecord chains Upper -> Prefix -> Record correctly."""
    r = ProcessedRecord(name="alice", prefix="TAG")
    result = r.process()
    assert result == ["TAG:RECORD:ALICE"], (
        f"ProcessedRecord(name='alice', prefix='TAG').process() should return "
        f"['TAG:RECORD:ALICE'], got {result}. "
        "Check that UpperMixin, PrefixMixin, and Record each call super().process()."
    )


def test_processed_record_different_name():
    """ProcessedRecord works with any name and prefix."""
    r = ProcessedRecord(name="bob", prefix="SYS")
    result = r.process()
    assert result == ["SYS:RECORD:BOB"], (
        f"ProcessedRecord(name='bob', prefix='SYS').process() should return "
        f"['SYS:RECORD:BOB'], got {result}."
    )


def test_mro_order():
    """ProcessedRecord MRO is: ProcessedRecord, UpperMixin, PrefixMixin, Record (no object)."""
    names = get_mro_names(ProcessedRecord)
    assert names == ["ProcessedRecord", "UpperMixin", "PrefixMixin", "Record"], (
        f"get_mro_names(ProcessedRecord) should return "
        f"['ProcessedRecord', 'UpperMixin', 'PrefixMixin', 'Record'], got {names}. "
        "Use [c.__name__ for c in cls.__mro__ if c is not object]."
    )


def test_get_mro_names_excludes_object():
    """get_mro_names excludes 'object' from the result."""
    names = get_mro_names(ProcessedRecord)
    assert "object" not in names, (
        f"get_mro_names should exclude 'object', but got {names}."
    )


def test_two_instances_independent():
    """Two ProcessedRecord instances are independent."""
    a = ProcessedRecord(name="alice", prefix="A")
    b = ProcessedRecord(name="bob", prefix="B")
    assert a.process() == ["A:RECORD:ALICE"]
    assert b.process() == ["B:RECORD:BOB"], (
        f"Two ProcessedRecord instances should be independent. "
        f"Got a={a.process()}, b={b.process()}."
    )


if __name__ == "__main__":
    r = ProcessedRecord(name="alice", prefix="TAG")
    print(r.process())
    print(get_mro_names(ProcessedRecord))
