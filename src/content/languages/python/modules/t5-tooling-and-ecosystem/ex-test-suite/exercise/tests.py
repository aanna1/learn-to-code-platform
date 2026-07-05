"""
Grader for ex-test-suite.

Each test is verified by:
  1. It passes with the correct TextProcessor (good_impl).
  2. It fails with a deliberately broken TextProcessor (broken_impl).
"""

import submission as sub


# ── Good / broken TextProcessor implementations ───────────────────────────────

class GoodTextProcessor:
    def __init__(self, text):
        if not text or not text.strip():
            raise ValueError("empty")
        self._text = text
    def word_count(self): return len(self._text.split())
    def uppercase(self): return self._text.upper()
    def truncate(self, max_len):
        if max_len < 1: raise ValueError(f"bad max_len {max_len}")
        return self._text[:max_len]
    def contains(self, s): return s in self._text


class BrokenTextProcessor:
    """Multiple bugs — every test should catch at least one."""
    def __init__(self, text):
        pass  # no validation — accepts empty/whitespace
    def word_count(self): return 0
    def uppercase(self): return self._text if hasattr(self, '_text') else ""
    def truncate(self, max_len): return "x" * max_len  # wrong result; accepts max_len=0
    def contains(self, s): return False


def _with_good(test_fn):
    """Run test_fn with TextProcessor and make_processor replaced by good implementations."""
    import contextlib
    orig_tp = sub.TextProcessor
    orig_mp = sub.make_processor
    sub.TextProcessor = GoodTextProcessor
    sub.make_processor = lambda t: GoodTextProcessor(t)
    try:
        test_fn()
        return "pass"
    except (AssertionError, ValueError, AttributeError) as e:
        return f"fail:{e}"
    finally:
        sub.TextProcessor = orig_tp
        sub.make_processor = orig_mp


def _with_broken(test_fn):
    orig_tp = sub.TextProcessor
    orig_mp = sub.make_processor
    sub.TextProcessor = BrokenTextProcessor
    sub.make_processor = lambda t: BrokenTextProcessor(t)
    try:
        test_fn()
        return "pass"
    except (AssertionError, ValueError, AttributeError) as e:
        return f"fail:{e}"
    finally:
        sub.TextProcessor = orig_tp
        sub.make_processor = orig_mp


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_test_empty_text_raises_exists():
    """test_empty_text_raises is defined."""
    assert callable(getattr(sub, "test_empty_text_raises", None))


def test_test_empty_text_raises_passes_good():
    """test_empty_text_raises passes with a correct TextProcessor."""
    result = _with_good(sub.test_empty_text_raises)
    assert result == "pass", (
        f"test_empty_text_raises should pass when TextProcessor('') raises ValueError, "
        f"but got: {result}. Use try/except ValueError around TextProcessor('')."
    )


def test_test_empty_text_raises_catches_broken():
    """test_empty_text_raises catches a TextProcessor that accepts empty strings."""
    result = _with_broken(sub.test_empty_text_raises)
    assert result != "pass", (
        "test_empty_text_raises should FAIL when TextProcessor('') does NOT raise, "
        "but it passed. Add `assert False, '...'` after the TextProcessor('') call."
    )


def test_test_whitespace_text_raises_exists():
    """test_whitespace_text_raises is defined."""
    assert callable(getattr(sub, "test_whitespace_text_raises", None))


def test_test_whitespace_text_raises_passes_good():
    """test_whitespace_text_raises passes with a correct TextProcessor."""
    result = _with_good(sub.test_whitespace_text_raises)
    assert result == "pass", (
        f"test_whitespace_text_raises should pass when TextProcessor('   ') raises ValueError, "
        f"but got: {result}."
    )


def test_test_whitespace_text_raises_catches_broken():
    """test_whitespace_text_raises catches a TextProcessor that accepts whitespace-only strings."""
    result = _with_broken(sub.test_whitespace_text_raises)
    assert result != "pass", (
        "test_whitespace_text_raises should FAIL when TextProcessor('   ') does NOT raise, "
        "but it passed."
    )


def test_test_word_count_exists():
    """test_word_count is defined."""
    assert callable(getattr(sub, "test_word_count", None))


def test_test_word_count_passes_good():
    """test_word_count passes with a correct TextProcessor."""
    result = _with_good(sub.test_word_count)
    assert result == "pass", (
        f"test_word_count should pass with a correct TextProcessor, but got: {result}. "
        "Use make_processor('hello world foo') and assert word_count() == 3."
    )


def test_test_word_count_catches_broken():
    """test_word_count catches a TextProcessor whose word_count always returns 0."""
    result = _with_broken(sub.test_word_count)
    assert result != "pass", (
        "test_word_count should FAIL when word_count() always returns 0, but it passed. "
        "Assert the exact word count, not just > 0."
    )


def test_test_uppercase_exists():
    """test_uppercase is defined."""
    assert callable(getattr(sub, "test_uppercase", None))


def test_test_uppercase_passes_good():
    """test_uppercase passes with a correct TextProcessor."""
    result = _with_good(sub.test_uppercase)
    assert result == "pass", (
        f"test_uppercase should pass with a correct TextProcessor, but got: {result}. "
        "Call make_processor('hello world') and assert uppercase() == 'HELLO WORLD'."
    )


def test_test_uppercase_catches_broken():
    """test_uppercase catches a TextProcessor whose uppercase returns an empty string."""
    result = _with_broken(sub.test_uppercase)
    assert result != "pass", (
        "test_uppercase should FAIL when uppercase() returns wrong results, but it passed. "
        "Assert the exact uppercased string."
    )


def test_test_truncate_exists():
    """test_truncate is defined."""
    assert callable(getattr(sub, "test_truncate", None))


def test_test_truncate_passes_good():
    """test_truncate passes with a correct TextProcessor."""
    result = _with_good(sub.test_truncate)
    assert result == "pass", (
        f"test_truncate should pass with a correct TextProcessor, but got: {result}. "
        "Call make_processor('hello world') and assert truncate(5) == 'hello'."
    )


def test_test_truncate_catches_broken():
    """test_truncate catches a TextProcessor whose truncate returns wrong content."""
    result = _with_broken(sub.test_truncate)
    assert result != "pass", (
        "test_truncate should FAIL when truncate returns wrong content, but it passed. "
        "Assert the exact truncated string, not just its length."
    )


def test_test_truncate_invalid_max_len_exists():
    """test_truncate_invalid_max_len is defined."""
    assert callable(getattr(sub, "test_truncate_invalid_max_len", None))


def test_test_truncate_invalid_max_len_passes_good():
    """test_truncate_invalid_max_len passes when truncate(0) raises ValueError."""
    result = _with_good(sub.test_truncate_invalid_max_len)
    assert result == "pass", (
        f"test_truncate_invalid_max_len should pass when truncate(0) raises ValueError, "
        f"but got: {result}. Use try/except ValueError around truncate(0)."
    )


def test_test_truncate_invalid_max_len_catches_broken():
    """test_truncate_invalid_max_len catches a TextProcessor that accepts max_len=0."""
    result = _with_broken(sub.test_truncate_invalid_max_len)
    assert result != "pass", (
        "test_truncate_invalid_max_len should FAIL when truncate(0) does NOT raise, "
        "but it passed. Add `assert False, '...'` after the truncate(0) call."
    )


if __name__ == "__main__":
    p = GoodTextProcessor("hello world foo")
    print("word_count:", p.word_count())
    print("uppercase:", p.uppercase())
    print("truncate(5):", p.truncate(5))
