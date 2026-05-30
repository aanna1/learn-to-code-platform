#!/usr/bin/env python3
"""Headless grader-discrimination check.

Usage:
    python grade_check.py <tests.py> <solution.py> [<starter.py>]

Runs every test_*() in <tests.py> against the solution (expects ALL PASS) and, if given, against
the starter (expects AT LEAST ONE FAIL). This proves the tests actually distinguish a correct
solution from the incomplete starter. No pytest required.

Exit code 0 only if: the solution passes all tests AND (no starter given OR the starter fails at
least one test). Any other outcome exits non-zero — fix it before the exercise checkpoint.
"""

import importlib.util
import io
import os
import shutil
import sys
import tempfile
import traceback


def _run_tests_against(tests_path, submission_path):
    """Run every test_*() in tests_path against submission_path.

    Mirrors the browser runtime (src/lib/languages/python/pyodide.worker.ts): the submission is
    imported as a real module named `submission`, and the tests are executed *inside the submission
    module's own namespace*. That single choice makes every test style behave here exactly as it
    does in the deployed app:
      - `import submission` / `from submission import x` / `importlib.reload(...)`,
      - direct calls to the submission's functions without importing,
      - monkeypatching a name via the test's `globals()` and having the submission's functions see
        it (they share one namespace).
    If these two ever diverge again, an exercise can pass here and still break in the browser -- so
    keep them in lock-step.

    Returns a list of (label, passed, message). Runs in an isolated temp dir with a clean module
    cache so the solution and starter runs don't contaminate each other.
    """
    workdir = tempfile.mkdtemp(prefix="gradecheck_")
    results = []
    saved_path = list(sys.path)
    saved_stdin = sys.stdin
    sys.modules.pop("submission", None)
    try:
        shutil.copyfile(submission_path, os.path.join(workdir, "submission.py"))
        sys.path.insert(0, workdir)
        # Feed EOF to any stray top-level input() so it errors instead of hanging.
        sys.stdin = io.StringIO("")
        try:
            import submission  # noqa: F401
            submission = sys.modules["submission"]
        except Exception:
            return [("(could not import submission.py)", False,
                     traceback.format_exc().splitlines()[-1])]
        ns = submission.__dict__
        try:
            with open(tests_path) as fh:
                exec(compile(fh.read(), "tests.py", "exec"), ns)
        except Exception:
            return [("(could not import tests.py)", False,
                     traceback.format_exc().splitlines()[-1])]
        test_names = sorted(n for n in ns if n.startswith("test_"))
        if not test_names:
            return [("(no tests found)", False, "tests.py defines no test_* functions")]
        for name in test_names:
            fn = ns.get(name)
            if not callable(fn):
                continue
            doc = (fn.__doc__ or "").strip().splitlines()
            label = doc[0].strip() if doc else name
            try:
                fn()
                results.append((label, True, ""))
            except AssertionError as e:
                results.append((label, False, str(e) or "assertion failed"))
            except Exception:
                last = traceback.format_exc().splitlines()[-1]
                results.append((label, False, "error: " + last))
    finally:
        sys.path[:] = saved_path
        sys.stdin = saved_stdin
        sys.modules.pop("submission", None)
        shutil.rmtree(workdir, ignore_errors=True)
    return results


def _report(title, results):
    print(f"\n=== {title} ===")
    for label, passed, msg in results:
        print(f"  [{'PASS' if passed else 'FAIL'}] {label}")
        if not passed and msg:
            print(f"         {msg}")
    n_pass = sum(1 for _, p, _ in results if p)
    print(f"  ({n_pass}/{len(results)} passed)")


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    tests_path, solution_path = argv[1], argv[2]
    starter_path = argv[3] if len(argv) > 3 else None

    sol = _run_tests_against(tests_path, solution_path)
    _report("SOLUTION (expect: all pass)", sol)
    sol_ok = len(sol) > 0 and all(p for _, p, _ in sol)

    starter_ok = True
    if starter_path:
        st = _run_tests_against(tests_path, starter_path)
        _report("STARTER (expect: >=1 fail)", st)
        starter_ok = any(not p for _, p, _ in st)

    print("\n--- summary ---")
    print(f"  solution passes all tests : {sol_ok}")
    if starter_path:
        print(f"  starter fails >=1 test    : {starter_ok}")
    ok = sol_ok and starter_ok
    print(f"  RESULT: {'OK' if ok else 'PROBLEM - fix before checkpoint'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
