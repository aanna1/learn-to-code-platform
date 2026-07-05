"use client";

/**
 * TEMPORARY C IDE harness (Phase C1) — the C analogue of the old `/dev/ide` route that
 * proved Python's IDE before it went live. It mounts the real <Ide> against the C language
 * WITHOUT registering C in the registry (via the `language` override prop), so the public
 * homepage/nav/outline stay Python-only until the C runtime is browser-verified.
 *
 * Remove this route in Phase C4 once C is registered (and `rm -rf .next` after deleting it,
 * per the route-deletion gotcha in CLAUDE.md).
 *
 * Needs cross-origin isolation (COOP/COEP, set globally in next.config.mjs for dev) so the
 * compiler loads under require-corp and interactive stdin can work once wired.
 */

import { Ide } from "@/components/ide/Ide";
import { c } from "@/lib/languages/c";

const STARTER = `#include <stdio.h>

int sum_to(int n) {
    int total = 0;
    /* TODO: add up the numbers from 1 to n */
    return total;
}

int main(void) {
    printf("sum_to(10) = %d\\n", sum_to(10));
    return 0;
}
`;

const SOLUTION = `#include <stdio.h>

int sum_to(int n) {
    int total = 0;
    for (int i = 1; i <= n; i++) {
        total += i;
    }
    return total;
}

int main(void) {
    printf("sum_to(10) = %d\\n", sum_to(10));
    return 0;
}
`;

const TESTS = `#include <stdio.h>
int sum_to(int n);

static void expect_eq(const char *name, int got, int want) {
    if (got == want) printf("__T__|%s|PASS\\n", name);
    else printf("__T__|%s|FAIL|expected %d but your code returned %d\\n", name, want, got);
}

int main(void) {
    expect_eq("sum_to(1) is 1", sum_to(1), 1);
    expect_eq("sum_to(5) is 15", sum_to(5), 15);
    expect_eq("sum_to(100) is 5050", sum_to(100), 5050);
    expect_eq("sum_to(0) is 0", sum_to(0), 0);
    return 0;
}
`;

const HINTS = [
  "A running total starts at 0, then adds each number from 1 up to n.",
  "A for-loop like `for (int i = 1; i <= n; i++)` visits every number in the range.",
  "Inside the loop, do `total += i;` so each number gets added on.",
];

export default function DevIdeCPage() {
  return (
    <main className="mx-auto flex h-[calc(100vh-3.5rem)] max-w-6xl flex-col gap-3 p-4">
      <div>
        <h1 className="text-lg font-semibold">/dev/ide-c — C runtime harness</h1>
        <p className="text-sm text-muted">
          Temporary Phase-C1 harness. Press Run to compile + run; Submit to grade against the
          hidden tests. Dev bundle is binji/wasm-clang (clang 8, no UBSan yet).
        </p>
      </div>
      <div className="min-h-0 flex-1">
        <Ide
          languageId="c"
          language={c}
          exercise={{ starter: STARTER, solution: SOLUTION, tests: TESTS, hints: HINTS }}
        />
      </div>
    </main>
  );
}
