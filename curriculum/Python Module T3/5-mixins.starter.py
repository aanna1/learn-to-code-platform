class Record:
    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = name

    def process(self) -> list:
        # TODO: return [f"Record:{self.name}"]
        pass


class UpperMixin:
    def process(self) -> list:
        # TODO: get super().process() and uppercase every string
        pass


class PrefixMixin:
    def __init__(self, prefix: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.prefix = prefix

    def process(self) -> list:
        # TODO: get super().process() and prepend self.prefix + ":" to each string
        pass


class ProcessedRecord(UpperMixin, PrefixMixin, Record):
    def __init__(self, name: str, prefix: str = "") -> None:
        super().__init__(name=name, prefix=prefix)


def get_mro_names(cls) -> list:
    # TODO: return list of class names in the MRO, excluding object
    pass


if __name__ == "__main__":
    r = ProcessedRecord(name="alice", prefix="TAG")
    print(r.process())              # ['TAG:RECORD:ALICE']
    print(get_mro_names(ProcessedRecord))
