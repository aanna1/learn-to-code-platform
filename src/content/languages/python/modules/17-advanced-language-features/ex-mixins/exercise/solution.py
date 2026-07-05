class Record:
    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = name

    def process(self) -> list:
        return [f"Record:{self.name}"]


class UpperMixin:
    def process(self) -> list:
        return [s.upper() for s in super().process()]


class PrefixMixin:
    def __init__(self, prefix: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.prefix = prefix

    def process(self) -> list:
        return [f"{self.prefix}:{s}" for s in super().process()]


class ProcessedRecord(UpperMixin, PrefixMixin, Record):
    def __init__(self, name: str, prefix: str = "") -> None:
        super().__init__(name=name, prefix=prefix)


def get_mro_names(cls) -> list:
    return [c.__name__ for c in cls.__mro__ if c is not object]


if __name__ == "__main__":
    r = ProcessedRecord(name="alice", prefix="TAG")
    print(r.process())              # ['TAG:RECORD:ALICE']
    print(get_mro_names(ProcessedRecord))
    # ['ProcessedRecord', 'UpperMixin', 'PrefixMixin', 'Record']
