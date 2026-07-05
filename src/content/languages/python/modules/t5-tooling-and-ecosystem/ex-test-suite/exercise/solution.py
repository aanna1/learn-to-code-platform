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


def test_empty_text_raises():
    try:
        TextProcessor("")
        assert False, "TextProcessor('') should raise ValueError"
    except ValueError:
        pass


def test_whitespace_text_raises():
    try:
        TextProcessor("   ")
        assert False, "TextProcessor('   ') should raise ValueError"
    except ValueError:
        pass


def test_word_count():
    p = make_processor("hello world foo")
    result = p.word_count()
    assert result == 3, f"word_count() should be 3, got {result}"


def test_uppercase():
    p = make_processor("hello world")
    result = p.uppercase()
    assert result == "HELLO WORLD", f"uppercase() should return 'HELLO WORLD', got {result!r}"


def test_truncate():
    p = make_processor("hello world")
    result = p.truncate(5)
    assert result == "hello", f"truncate(5) should return 'hello', got {result!r}"


def test_truncate_invalid_max_len():
    p = make_processor("hello")
    try:
        p.truncate(0)
        assert False, "truncate(0) should raise ValueError"
    except ValueError:
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
