import sys
import os
import importlib

def _load():
    here = os.path.dirname(__file__)
    if here not in sys.path:
        sys.path.insert(0, here)
    name = "submission"
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)


def test_ask_returns_string():
    """ask() returns a string."""
    m = _load()
    result = m.ask("Will it rain?")
    assert isinstance(result, str), (
        f"Expected a string but got {type(result).__name__!r}. "
        "Use random.choice(RESPONSES) and return the result."
    )


def test_ask_returns_valid_response():
    """ask() always returns one of the 20 responses."""
    m = _load()
    for _ in range(50):
        result = m.ask("Test?")
        assert result in m.RESPONSES, (
            f"Got {result!r}, which is not in RESPONSES. "
            "Make sure you're returning random.choice(RESPONSES)."
        )


def test_responses_list_unchanged():
    """RESPONSES contains exactly 20 entries."""
    m = _load()
    assert len(m.RESPONSES) == 20, (
        f"Expected RESPONSES to have 20 items but got {len(m.RESPONSES)}. "
        "Keep the list exactly as given."
    )


def test_ask_ignores_question():
    """ask() works with any question string."""
    m = _load()
    for q in ["?", "", "a" * 200, "Hello!"]:
        result = m.ask(q)
        assert isinstance(result, str) and result in m.RESPONSES, (
            f"ask({q!r}) returned {result!r}, which is not in RESPONSES."
        )


def test_positive_returns_bool():
    """positive() returns a bool."""
    m = _load()
    result = m.positive("Test?")
    assert isinstance(result, bool), (
        f"Expected a bool but got {type(result).__name__!r}. "
        "Return True or False from positive()."
    )


def test_positive_true_for_first_ten():
    """positive() returns True when ask() returns a first-ten response."""
    import unittest.mock as mock
    m = _load()
    for resp in m.RESPONSES[:10]:
        with mock.patch.object(m, "ask", return_value=resp):
            assert m.positive("Q?") is True, (
                f"positive() should return True for {resp!r} (a positive response) "
                "but returned False."
            )


def test_positive_false_for_last_ten():
    """positive() returns False when ask() returns a last-ten response."""
    import unittest.mock as mock
    m = _load()
    for resp in m.RESPONSES[10:]:
        with mock.patch.object(m, "ask", return_value=resp):
            assert m.positive("Q?") is False, (
                f"positive() should return False for {resp!r} (a non-positive response) "
                "but returned True."
            )


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                print(f"FAIL  {name}: {e}")
            except Exception as e:
                print(f"ERROR {name}: {e}")
