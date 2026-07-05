import json
import urllib.request
from unittest.mock import patch, MagicMock

ENDPOINT = "https://monitor.example.com/alerts"
VALID_LEVELS = {"info", "warning", "error"}


def send_alert(message: str, level: str = "info") -> dict:
    """POST an alert to the monitoring endpoint.

    Returns the parsed JSON response body.
    Raises ValueError if level is not 'info', 'warning', or 'error'.
    """
    if level not in VALID_LEVELS:
        raise ValueError(f"level must be one of {sorted(VALID_LEVELS)}, got {level!r}")
    payload = json.dumps({"message": message, "level": level}).encode()
    req = urllib.request.Request(
        ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())


# ── Helper ────────────────────────────────────────────────────────────────────

def make_mock_response(body_bytes: bytes) -> MagicMock:
    """Return a MagicMock that works as a context-manager HTTP response."""
    mock = MagicMock()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    mock.read.return_value = body_bytes
    return mock


# ── Write your tests below ────────────────────────────────────────────────────

def test_send_alert_posts_to_endpoint():
    # patch urllib.request.urlopen and assert the right URL was called
    pass


def test_send_alert_returns_parsed_json():
    # mock urlopen to return make_mock_response(b'{"status": "ok"}')
    # and assert send_alert returns {"status": "ok"}
    pass


def test_send_alert_invalid_level():
    # assert that send_alert("msg", "critical") raises ValueError
    pass


# ── Runner (do not edit) ──────────────────────────────────────────────────────
if __name__ == "__main__":
    for fn in [
        test_send_alert_posts_to_endpoint,
        test_send_alert_returns_parsed_json,
        test_send_alert_invalid_level,
    ]:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            print(f"FAIL  {fn.__name__}: {e}")
        except Exception as e:
            print(f"ERROR {fn.__name__}: {type(e).__name__}: {e}")
