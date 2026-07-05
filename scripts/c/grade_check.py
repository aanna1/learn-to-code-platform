#!/usr/bin/env python3
"""Headless grader-discrimination check for C exercises.

Usage:
    python grade_check.py <tests.c> <solution.c> [<starter.c>]

The C analogue of the Python skill's grade_check.py. It compiles the submission together with the
hidden test harness and runs the result, then checks that the tests actually DISCRIMINATE: the
solution must pass every case, and (if given) the starter must fail at least one. That is what
makes an exercise a real checkpoint rather than a rubber stamp.

The compile/run model here is byte-for-byte the same one the in-browser worker uses
(src/lib/languages/c/c.worker.ts), so "passes grade_check" <=> "passes in the browser":

  * SEPARATE-COMPILE. The submission and tests.c are compiled to separate objects and linked.
    The submission is compiled with `-Dmain=__student_main__`, which neutralizes any `main()` the
    learner left in for the Run experience so it can't collide with the harness's own `main()`.
    This is the C mirror of how the Python runner imports the submission as a module and skips its
    `if __name__ == "__main__":` block.
  * The hidden tests.c owns `main()`, declares the submission's prototypes, calls them, and prints
    ONE machine-readable line per case to stdout:
        __T__|<name>|PASS
        __T__|<name>|FAIL|<message>
  * Builds use `-fsanitize=undefined` in NON-trapping mode, so undefined behavior prints a
    readable message (fed to the errorExplainer in the browser) and the case is counted as failed.

This environment has no browser, so the compiler proxy is `zig cc` (a Clang driver) targeting
wasm32-wasi, run under Node's WASI -- exactly the C0-spike setup. The flags below match what the
browser toolchain compiles with; keep the two in lock-step.

Exit code 0 only if the solution passes all tests AND (no starter given OR the starter fails at
least one). Any other outcome exits non-zero -- fix it before shipping the exercise.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WASI_RUNNER = os.path.join(HERE, "run_wasi.mjs")

# The compiler. `zig cc` is a Clang driver with a bundled wasi-libc sysroot, so it stands in for
# the browser's clang-wasm without needing a network or a sysroot install.
CC = [sys.executable, "-m", "ziglang", "cc"]

# Compile flags shared by Run and Submit in the browser. Keep in sync with c.worker.ts.
# `-fno-sanitize-trap=undefined` makes UBSan print a human-readable line ("signed integer
# overflow: ...") to stderr before aborting, instead of a bare `unreachable` trap -- that text is
# what the browser feeds the errorExplainer as an UndefinedBehavior explanation.
TARGET = "wasm32-wasi"
SANITIZE = ["-fsanitize=undefined", "-fno-sanitize-trap=undefined"]
COMMON_CFLAGS = ["-target", TARGET, "-std=c11", "-Wall", "-Wextra", "-O0"] + SANITIZE

# Per-program wall-clock cap so an infinite loop in a submission can't hang grading.
RUN_TIMEOUT_S = 10
COMPILE_TIMEOUT_S = 60

_T_LINE = re.compile(r"^__T__\|([^|]*)\|(PASS|FAIL)(?:\|(.*))?$")


def _run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def _compile_and_link(submission_path, tests_path, out_wasm):
    """Compile {submission, tests} per the contract. Returns (ok, error_message)."""
    workdir = os.path.dirname(out_wasm)
    sub_o = os.path.join(workdir, "submission.o")
    tests_o = os.path.join(workdir, "tests.o")
    try:
        # Submission TU: rename any student main() out of the way.
        r = _run(CC + COMMON_CFLAGS + ["-Dmain=__student_main__", "-c", submission_path, "-o", sub_o],
                 timeout=COMPILE_TIMEOUT_S)
        if r.returncode != 0:
            return False, _first_diag(r.stderr)
        # Test harness TU: keep its real main().
        r = _run(CC + COMMON_CFLAGS + ["-c", tests_path, "-o", tests_o], timeout=COMPILE_TIMEOUT_S)
        if r.returncode != 0:
            return False, _first_diag(r.stderr)
        # Link.
        r = _run(CC + ["-target", TARGET] + SANITIZE + [sub_o, tests_o, "-o", out_wasm],
                 timeout=COMPILE_TIMEOUT_S)
        if r.returncode != 0:
            return False, _first_diag(r.stderr)
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "compilation timed out"


def _first_diag(stderr):
    """The first error: line from the compiler, for a compact report."""
    for line in stderr.splitlines():
        if "error:" in line:
            return line.strip()
    return (stderr.strip().splitlines() or ["compile failed"])[0]


def _run_wasm(out_wasm, stdin_path=None):
    """Run the module under WASI. Returns (stdout, stderr, returncode, timed_out)."""
    cmd = ["node", "--no-warnings", WASI_RUNNER, out_wasm]
    if stdin_path:
        cmd.append(stdin_path)
    try:
        r = _run(cmd, timeout=RUN_TIMEOUT_S)
        return r.stdout, r.stderr, r.returncode, False
    except subprocess.TimeoutExpired as e:
        return (e.stdout or ""), (e.stderr or ""), 124, True


def _parse_results(stdout):
    """Pull __T__|name|PASS/FAIL|msg lines into (label, passed, message) tuples."""
    out = []
    for line in stdout.splitlines():
        m = _T_LINE.match(line.strip())
        if m:
            name, verdict, msg = m.group(1), m.group(2), (m.group(3) or "")
            out.append((name, verdict == "PASS", msg))
    return out


def grade(tests_path, submission_path):
    """Compile+run the submission against the harness; return [(label, passed, message)]."""
    workdir = tempfile.mkdtemp(prefix="cgrade_")
    try:
        out_wasm = os.path.join(workdir, "out.wasm")
        ok, err = _compile_and_link(submission_path, tests_path, out_wasm)
        if not ok:
            return [("(does not compile)", False, err)]
        stdout, stderr, rc, timed_out = _run_wasm(out_wasm)
        results = _parse_results(stdout)
        if timed_out:
            results.append(("(timed out)", False, f"program exceeded {RUN_TIMEOUT_S}s -- possible infinite loop"))
        elif rc != 0:
            # A trap (UBSan trap, OOB, div-by-zero) or non-zero exit: any case that never printed
            # its line is effectively failed, and we surface the crash itself as a failure.
            detail = ""
            # Prefer a readable UBSan/diagnostic line over the generic trap marker.
            markers = ("runtime error:", "signed integer overflow", "out of bounds",
                       "panic:", "division by zero", "shift")
            for line in stderr.splitlines():
                if any(mk in line for mk in markers):
                    detail = line.replace("panic:", "undefined behavior:").strip()
                    break
            if not detail:
                for line in stderr.splitlines():
                    if line.startswith("__TRAP__"):
                        detail = line.replace("__TRAP__", "trap:").strip()
                        break
            results.append((f"(program crashed, exit {rc})", False, detail or stderr.strip()[:200]))
        if not results:
            return [("(no test output)", False, "the harness printed no __T__ lines")]
        return results
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


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

    sol = grade(tests_path, solution_path)
    _report("SOLUTION (expect: all pass)", sol)
    sol_ok = len(sol) > 0 and all(p for _, p, _ in sol)

    starter_ok = True
    if starter_path:
        st = grade(tests_path, starter_path)
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
