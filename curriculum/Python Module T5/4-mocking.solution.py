import json
import urllib.request
from unittest.mock import patch, MagicMock

ENDPOINT = "https://monitor.example.com/alerts"
VALID_LEVELS = {"info", "warning", "error"}


def send_alert(message: str, level: str = "info") -> dict:
    """POST an alert to the monitoring endpoint."""
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


def make_mock_response(body_bytes: bytes) -> MagicMock:
    mock = MagicMock()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    mock.read.return_value = body_bytes
    return mock


def test_send_alert_posts_to_endpoint():
    with patch("urllib.request.urlopen", return_value=make_mock_response(b'{"ok":true}')) as mock_open:
        send_alert("disk full", "warning")
    mock_open.assert_called_once()
    req_arg = mock_open.call_args[0][0]
    assert req_arg.full_url == ENDPOINT, (
        f"Expected URL {ENDPOINT!r}, got {req_arg.full_url!r}"
    )
    assert b"disk full" in req_arg.data, (
        f"Expected 'disk full' in request data, got {req_arg.data!r}"
    )


def test_send_alert_returns_parsed_json():
    with patch("urllib.request.urlopen", return_value=make_mock_response(b'{"status": "ok"}')):
        result = send_alert("test", "info")
    assert result == {"status": "ok"}, f"Expected {{'status': 'ok'}}, got {result!r}"


def test_send_alert_invalid_level():
    try:
        send_alert("msg", "critical")
        assert False, "Expected ValueError for invalid level"
    except ValueError:
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
