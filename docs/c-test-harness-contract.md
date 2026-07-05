# C Test-Harness Contract (Phase C2)

The C analogue of Python's `test_*` convention. It is the rule that makes **"passes
`scripts/c/grade_check.py` ⟺ passes Submit in the browser"** true, so author every C exercise
to it and keep the headless grader and the browser worker (`src/lib/languages/c/c.worker.ts`,
Phase C1) compiling/running submissions the *same* way.

Validated headlessly in the sandbox with `zig cc` (a Clang driver) → `wasm32-wasi` → Node WASI,
the same proxy the C0 spike used. The browser will use clang-wasm with the identical flags.

## Files per exercise

Mirrors Python's layout, with `.c` instead of `.py`:

```
<lessonId>/exercise/
  prompt.mdx      # the task, browser-framed ("press Run")
  starter.c       # what the learner starts from — must FAIL ≥1 test
  solution.c      # reference — must PASS every test
  tests.c         # hidden harness (below) — never shown to the learner
  hints.json      # progressive hints
```

## The harness (`tests.c`)

1. **`tests.c` owns `main()`.** It declares the prototypes the exercise asks the learner to
   implement, calls them, and checks results.
2. **One machine-readable line per case**, printed to stdout:
   ```
   __T__|<name>|PASS
   __T__|<name>|FAIL|<short, beginner-friendly message>
   ```
   `<name>` is the display name in the results panel; the `FAIL` message shows only on failure.
3. The learner's `submission.c` is compiled with **`-Dmain=__student_main__`**, which renames any
   `main()` they kept for the Run experience so it can't collide with the harness's `main()`. This
   is the C mirror of how the Python runner imports the submission as a module and skips its
   `if __name__ == "__main__":` block.

A minimal harness:

```c
#include <stdio.h>
int sum_to(int n);   /* implemented by submission.c */

static void expect_eq(const char *name, int got, int want) {
    if (got == want) printf("__T__|%s|PASS\n", name);
    else printf("__T__|%s|FAIL|expected %d but your code returned %d\n", name, want, got);
}

int main(void) {
    expect_eq("sum_to(5) is 15", sum_to(5), 15);
    return 0;
}
```

A full worked example lives in `scripts/c/example/` (`tests.c`, `solution.c`, `starter.c`).

## Build model (must match worker ⟺ grader)

**Separate-compile, then link** (the C0 spike's recommended default):

```
cc <CFLAGS> -Dmain=__student_main__ -c submission.c -o submission.o   # student main neutralized
cc <CFLAGS>                          -c tests.c      -o tests.o        # harness keeps its main
cc -target wasm32-wasi <SANITIZE> submission.o tests.o -o out.wasm     # link
```

`<CFLAGS>` = `-target wasm32-wasi -std=c11 -Wall -Wextra -O0 -fsanitize=undefined
-fno-sanitize-trap=undefined`.

- `-Dmain=...` is applied **only to the submission TU** (applying it globally renames the
  harness's `main` too and the link fails with a duplicate symbol — this was the first bug found
  and is why compilation is separate, not a single `cc a.c b.c`).
- `-fsanitize=undefined -fno-sanitize-trap=undefined` makes undefined behavior print a readable
  line (`signed integer overflow: 2147483647 + 5 cannot be represented in type 'int'`) to stderr
  before aborting. That text is fed to the `errorExplainer` as an `UndefinedBehavior` explanation.

### Grading verdict

- **Compile failure** → the whole submission fails (one synthetic `(does not compile)` case with
  the first `error:` line).
- **Run, exit 0, every `__T__` line `PASS`** → pass.
- **Trap / non-zero exit** (UBSan abort, OOB on a fixed-size local array, div-by-zero, an
  `assert`) → fail; the readable UBSan/diagnostic line is surfaced as the message.
- **No output / timeout** (e.g. infinite loop, 10 s cap) → fail.

## Sanitizer reach (from the C0 spike — don't over-promise)

UBSan **works** on `wasm32-wasi` and catches a useful UB subset: signed overflow, shifts,
**fixed-size local-array** out-of-bounds, misalignment, div-by-zero. **AddressSanitizer is
unavailable** on this target, so **heap** OOB, use-after-free, and leaks are **not** detected on
the browser path. Grading v1 = compiler warnings (`-Wall -Wextra`) + hidden tests + non-trap
UBSan. Real heap/leak authenticity exists only on the heavy `v86` route (out of scope).

## Running the grader

```
python3 scripts/c/grade_check.py <tests.c> <solution.c> [<starter.c>]
```

Exit 0 only if the solution passes everything **and** (no starter given **or** the starter fails
≥1) — i.e. the tests genuinely discriminate. Requires `pip install --break-system-packages
ziglang` and Node (for the WASI runner `scripts/c/run_wasi.mjs`). Run it on every exercise before
it ships, exactly as Python exercises run the Python `grade_check.py`.
