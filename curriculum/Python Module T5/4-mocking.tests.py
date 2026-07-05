"""
Grader for ex-mocking.

Each of the three tests is verified by:
  1. Running the learner's test with the CORRECT send_alert — it must pass.
  2. Running the learner's test with a BROKEN send_alert — it must fail.
"""

import json
import urllib.request
from unittest.mock import patch, MagicMock, call
import submission as sub


# ── Good / broken send_alert implementations ─────────────────────────────────

def _good_send_alert(message: str, level: str = "info") -> dict:
    if level not in {"info", "warning", "error"}:
        raise ValueError(f"bad level: {level!r}")
    payload = json.dumps({"message": message, "level": level}).encode()
    req = urllib.request.Request(
        sub.ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())


def _broken_no_network_call(message: str, level: str = "info") -> dict:
    """Skips urlopen entirely — test_send_alert_posts_to_endpoint should catch it."""
    if level not in {"info", "warning", "error"}:
        raise ValueError()
    return {"ok": True}


def _broken_wrong_url(message: str, level: str = "info") -> dict:
    """Calls urlopen but with the wrong URL."""
    if level not in {"info", "warning", "error"}:
        raise ValueError()
    fake = MagicMock()
    fake.__enter__ = lambda s: s
    fake.__exit__ = MagicMock(return_value=False)
    fake.read.return_value = b'{"ok": true}'
    with urllib.request.urlopen("https://wrong.example.com") as r:
        return json.loads(r.read())


def _broken_no_validation(message: str, level: str = "info") -> dict:
    """Accepts any level — test_send_alert_invalid_level should catch it."""
    fake = MagicMock()
    fake.__enter__ = lambda s: s
    fake.__exit__ = MagicMock(return_value=False)
    fake.read.return_value = b'{"ok": true}'
    with urllib.request.urlopen(urllib.request.Request(sub.ENDPOINT, data=b"x")) as r:
        return json.loads(r.read())


def _broken_returns_wrong_json(message: str, level: str = "info") -> dict:
    """Returns a hardcoded wrong dict — test_send_alert_returns_parsed_json should catch it."""
    if level not in {"info", "warning", "error"}:
        raise ValueError()
    payload = json.dumps({"message": message, "level": level}).encode()
    with urllib.request.urlopen(
        urllib.request.Request(sub.ENDPOINT, data=payload)
    ) as r:
        return {"wrong": "response"}


# ── Helper ────────────────────────────────────────────────────────────────────

def _patch_send_alert(replacement):
    import contextlib
    @contextlib.contextmanager
    def _ctx():
        original = sub.send_alert
        sub.send_alert = replacement
        try:
            yield
        finally:
            sub.send_alert = original
    return _ctx()


def _run_with_mock_urlopen(test_fn, response_body=b'{"ok":true}'):
    """Run test_fn with urllib.request.urlopen patched to return a canned response."""
    mock_resp = sub.make_mock_response(response_body)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        test_fn()


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_test_send_alert_posts_to_endpoint_exists():
    """test_send_alert_posts_to_endpoint is defined."""
    assert callable(getattr(sub, "test_send_alert_posts_to_endpoint", None)), (
        "Define test_send_alert_posts_to_endpoint()."
    )


def test_test_send_alert_posts_passes_good_impl():
    """test_send_alert_posts_to_endpoint passes with a correct implementation."""
    with _patch_send_alert(_good_send_alert):
        try:
            _run_with_mock_urlopen(sub.test_send_alert_posts_to_endpoint)
        except AssertionError as e:
            assert False, (
                f"test_send_alert_posts_to_endpoint should pass with a correct send_alert, "
                f"but failed: {e}"
            )


def test_test_send_alert_posts_catches_no_network_call():
    """test_send_alert_posts_to_endpoint catches a send_alert that never calls urlopen."""
    with _patch_send_alert(_broken_no_network_call):
        with patch("urllib.request.urlopen", return_value=sub.make_mock_response(b'{"ok":true}')) as mock_open:
            try:
                sub.test_send_alert_posts_to_endpoint()
                assert False, (
                    "test_send_alert_posts_to_endpoint should FAIL when send_alert never "
                    "calls urlopen, but it passed. "
                    "Use mock_open.assert_called_once() inside your test."
                )
            except AssertionError as e:
                if "should FAIL" in str(e):
                    raise


def test_test_send_alert_returns_json_exists():
    """test_send_alert_returns_parsed_json is defined."""
    assert callable(getattr(sub, "test_send_alert_returns_parsed_json", None)), (
        "Define test_send_alert_returns_parsed_json()."
    )


def test_test_send_alert_returns_json_passes_good_impl():
    """test_send_alert_returns_parsed_json passes with a correct implementation."""
    with _patch_send_alert(_good_send_alert):
        try:
            _run_with_mock_urlopen(
                sub.test_send_alert_returns_parsed_json,
                b'{"status": "ok"}',
            )
        except AssertionError as e:
            assert False, (
                f"test_send_alert_returns_parsed_json should pass with a correct "
                f"send_alert, but failed: {e}"
            )


def test_test_send_alert_returns_json_catches_wrong_return():
    """test_send_alert_returns_parsed_json catches a send_alert that returns the wrong dict."""
    with _patch_send_alert(_broken_returns_wrong_json):
        with patch("urllib.request.urlopen", return_value=sub.make_mock_response(b'{"status":"ok"}')):
            try:
                sub.test_send_alert_returns_parsed_json()
                assert False, (
                    "test_send_alert_returns_parsed_json should FAIL when send_alert "
                    "returns a wrong dict, but it passed. "
                    "Assert that the return value equals {'status': 'ok'}."
                )
            except AssertionError as e:
                if "should FAIL" in str(e):
                    raise


def test_test_send_alert_invalid_level_exists():
    """test_send_alert_invalid_level is defined."""
    assert callable(getattr(sub, "test_send_alert_invalid_level", None)), (
        "Define test_send_alert_invalid_level()."
    )


def test_test_send_alert_invalid_level_passes_good_impl():
    """test_send_alert_invalid_level passes when send_alert raises for bad levels."""
    with _patch_send_alert(_good_send_alert):
        try:
            sub.test_send_alert_invalid_level()
        except AssertionError as e:
            assert False, (
                f"test_send_alert_invalid_level should pass when send_alert raises "
                f"ValueError for 'critical', but failed: {e}"
            )


def test_test_send_alert_invalid_level_catches_no_validation():
    """test_send_alert_invalid_level catches a send_alert with no level validation."""
    with _patch_send_alert(_broken_no_validation):
        with patch("urllib.request.urlopen", return_value=sub.make_mock_response(b'{"ok":true}')):
            try:
                sub.test_send_alert_invalid_level()
                assert False, (
                    "test_send_alert_invalid_level should FAIL when send_alert accepts "
                    "'critical' without raising, but it passed. "
                    "Use try/except ValueError and assert False if no exception is thrown."
                )
            except AssertionError as e:
                if "should FAIL" in str(e):
                    raise


if __name__ == "__main__":
    r = _good_send_alert.__wrapped__ if hasattr(_good_send_alert, '__wrapped__') else None
    print("ENDPOINT:", sub.ENDPOINT)
