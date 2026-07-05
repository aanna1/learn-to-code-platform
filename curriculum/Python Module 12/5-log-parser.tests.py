LOG = """\
2026-03-14 09:14:22 INFO  user=alice ip=10.0.0.5 path=/login status=200
2026-03-14 09:14:23 ERROR user=bob   ip=10.0.0.9 path=/admin status=403
2026-03-14 09:14:25 ERROR user=carol ip=10.0.0.9 path=/admin status=403
2026-03-14 09:14:30 INFO  user=alice ip=10.0.0.5 path=/home  status=200
2026-03-14 09:14:35 ERROR user=dave  ip=10.0.0.7 path=/login status=401
2026-03-14 09:14:40 ERROR user=eve   ip=10.0.0.9 path=/api   status=429
"""


def test_counts_repeated_ip():
    "counts an IP that appears in multiple 4xx lines"
    result = count_rejected_ips(LOG)
    assert result.get("10.0.0.9") == 3, \
        f"10.0.0.9 appears in three 4xx lines (403, 403, 429) but got {result.get('10.0.0.9')!r}. " \
        "Make sure you increment the count each time the IP appears, not just record it once."

def test_counts_single_occurrence():
    "counts an IP that appears in exactly one 4xx line"
    result = count_rejected_ips(LOG)
    assert result.get("10.0.0.7") == 1, \
        f"10.0.0.7 appears in one 4xx line (401) but got {result.get('10.0.0.7')!r}."

def test_ignores_2xx():
    "ignores lines with 2xx status codes"
    result = count_rejected_ips(LOG)
    assert "10.0.0.5" not in result, \
        f"10.0.0.5 only appears in 200-status lines, so it should not be in the result. " \
        f"Got {result}. Check that you're filtering for status.startswith('4')."

def test_returns_dict():
    "function returns a dict"
    result = count_rejected_ips(LOG)
    assert isinstance(result, dict), \
        f"count_rejected_ips should return a dict, but got {type(result).__name__!r}."

def test_empty_log():
    "returns an empty dict for an empty string"
    result = count_rejected_ips("")
    assert result == {}, \
        f"Expected {{}} for an empty log but got {result!r}."

def test_only_2xx_log():
    "returns an empty dict when all lines are 2xx"
    log = "2026-03-14 09:00:00 INFO user=alice ip=10.0.0.1 path=/home status=200\n"
    result = count_rejected_ips(log)
    assert result == {}, \
        f"No 4xx lines means no rejected IPs, but got {result!r}."

def test_values_are_ints():
    "counts are integers, not strings"
    result = count_rejected_ips(LOG)
    for ip, count in result.items():
        assert isinstance(count, int), \
            f"Count for {ip!r} should be an int, but got {type(count).__name__!r}. " \
            "Use counts.get(ip, 0) + 1 to increment."
