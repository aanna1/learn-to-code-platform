import io
import contextlib


# ── helpers ──────────────────────────────────────────────────────────────────

def _capture(fn, *args, **kwargs):
    """Run fn(*args) and return (return_value, stdout_lines)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = fn(*args, **kwargs)
    lines = [l for l in buf.getvalue().splitlines() if l.strip()]
    return result, lines


class _patch:
    """Temporarily replace a name in the test module's globals."""
    def __init__(self, name, replacement):
        self.name = name
        self.replacement = replacement
        self.original = None

    def __enter__(self):
        self.original = globals().get(self.name)
        globals()[self.name] = self.replacement
        return self

    def __exit__(self, *_):
        globals()[self.name] = self.original


# ── roll_die ─────────────────────────────────────────────────────────────────

def test_roll_die_range():
    "roll_die always returns a value between 1 and 6 inclusive"
    for _ in range(200):
        v = roll_die()
        assert 1 <= v <= 6, (
            f"roll_die() returned {v!r}, which is outside 1–6. "
            "Use random.randint(1, 6)."
        )


def test_roll_die_returns_int():
    "roll_die returns an int"
    v = roll_die()
    assert isinstance(v, int), (
        f"roll_die() should return an int, got {type(v).__name__!r}"
    )


# ── roll_n ───────────────────────────────────────────────────────────────────

def test_roll_n_calls_roll_die():
    "roll_n(n) calls roll_die n times, not random.randint directly"
    call_count = [0]
    def fake_roll_die():
        call_count[0] += 1
        return 3

    with _patch("roll_die", fake_roll_die):
        result = roll_n(4)

    assert call_count[0] == 4, (
        f"roll_n(4) should call roll_die() exactly 4 times, called {call_count[0]} time(s). "
        "Use a loop that calls roll_die() on each iteration."
    )
    assert result == 12, (
        f"roll_n(4) with each roll_die() returning 3 should give 12, got {result!r}"
    )


def test_roll_n_total():
    "roll_n returns the sum of the individual die rolls"
    rolls = [2, 5, 1]
    idx = [0]
    def fake_roll_die():
        v = rolls[idx[0]]
        idx[0] += 1
        return v

    with _patch("roll_die", fake_roll_die):
        result = roll_n(3)

    assert result == 8, (
        f"roll_n(3) with rolls [2, 5, 1] should return 8, got {result!r}. "
        "Make sure you're summing the results, not returning the last roll."
    )


def test_roll_n_one():
    "roll_n(1) returns the result of a single roll"
    with _patch("roll_die", lambda: 6):
        result = roll_n(1)
    assert result == 6, (
        f"roll_n(1) should return the value of one roll (6), got {result!r}"
    )


# ── play_round ────────────────────────────────────────────────────────────────

def test_play_round_prints_format():
    "play_round prints the correct format"
    with _patch("roll_n", lambda n: 11):
        _, lines = _capture(play_round, "Alice", 3)

    assert len(lines) >= 1, "play_round should print one line of output."
    assert lines[0] == "Alice rolled 3 dice and got 11", (
        f"Expected 'Alice rolled 3 dice and got 11', got {lines[0]!r}. "
        "Check spelling, spacing, and that you're using the player_name and num_dice parameters."
    )


def test_play_round_returns_total():
    "play_round returns the total rolled"
    with _patch("roll_n", lambda n: 14):
        result, _ = _capture(play_round, "Bob", 3)
    assert result == 14, (
        f"play_round should return the total (14), got {result!r}. "
        "Make sure you return the result of roll_n, not just print it."
    )


def test_play_round_calls_roll_n():
    "play_round calls roll_n with num_dice"
    calls = []
    def fake_roll_n(n):
        calls.append(n)
        return 9

    with _patch("roll_n", fake_roll_n):
        _capture(play_round, "Alice", 3)

    assert calls == [3], (
        f"play_round('Alice', 3) should call roll_n(3), but roll_n was called with: {calls}"
    )


# ── main / winner logic ───────────────────────────────────────────────────────

def test_main_alice_wins():
    "main prints 'Alice wins!' when Alice's total is higher"
    results = [15, 10]
    idx = [0]
    def fake_play_round(name, n):
        v = results[idx[0]]; idx[0] += 1
        return v

    with _patch("play_round", fake_play_round):
        _, lines = _capture(main)

    assert any("Alice wins!" in l for l in lines), (
        f"When Alice scores 15 and Bob scores 10, expected 'Alice wins!' in output. Got: {lines}"
    )


def test_main_bob_wins():
    "main prints 'Bob wins!' when Bob's total is higher"
    results = [8, 14]
    idx = [0]
    def fake_play_round(name, n):
        v = results[idx[0]]; idx[0] += 1
        return v

    with _patch("play_round", fake_play_round):
        _, lines = _capture(main)

    assert any("Bob wins!" in l for l in lines), (
        f"When Alice scores 8 and Bob scores 14, expected 'Bob wins!' in output. Got: {lines}"
    )


def test_main_tie():
    "main prints \"It's a tie!\" when totals are equal"
    results = [12, 12]
    idx = [0]
    def fake_play_round(name, n):
        v = results[idx[0]]; idx[0] += 1
        return v

    with _patch("play_round", fake_play_round):
        _, lines = _capture(main)

    assert any("tie" in l.lower() for l in lines), (
        f"When both players score 12, expected \"It's a tie!\" in output. Got: {lines}"
    )
