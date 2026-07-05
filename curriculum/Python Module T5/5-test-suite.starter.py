class TextProcessor:
    def __init__(self, text: str):
        if not text or not text.strip():
            raise ValueError("text must not be empty or whitespace-only")
        self._text = text

    def word_count(self) -> int:
        return len(self._text.split())

    def uppercase(self) -> str:
        return self._text.upper()

    def truncate(self, max_len: int) -> str:
        if max_len < 1:
            raise ValueError(f"max_len must be >= 1, got {max_len}")
        return self._text[:max_len]

    def contains(self, substring: str) -> bool:
        return substring in self._text


def make_processor(text: str) -> TextProcessor:
    """Fixture: return a TextProcessor for the given text."""
    return TextProcessor(text)


# ── Write your tests below ────────────────────────────────────────────────────

def test_empty_text_raises():
    pass


def test_whitespace_text_raises():
    pass


def test_word_count():
    pass


def test_uppercase():
    pass


def test_truncate():
    pass


def test_truncate_invalid_max_len():
    pass


# ── Runner (do not edit) ──────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        test_empty_text_raises,
        test_whitespace_text_raises,
        test_word_count,
        test_uppercase,
        test_truncate,
        test_truncate_invalid_max_len,
    ]
    for fn in tests:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            print(f"FAIL  {fn.__name__}: {e}")
        except Exception as e:
            print(f"ERROR {fn.__name__}: {type(e).__name__}: {e}")
