/*
 * Example hidden test harness — the canonical shape every C exercise's tests.c follows.
 *
 * Contract:
 *   - This file owns main(). The learner's submission.c is compiled with -Dmain=__student_main__
 *     so any main() they kept for the Run experience can't collide with this one.
 *   - Declare the submission's functions (the prototypes the exercise asks the learner to write).
 *   - For each case, print exactly one line:
 *         __T__|<name>|PASS
 *         __T__|<name>|FAIL|<short, friendly message>
 *   - The first field after __T__ is the display name shown in the results panel; the FAIL message
 *     is shown only on failure, so write it for a beginner.
 */
#include <stdio.h>

/* Prototype(s) under test — implemented by the learner's submission.c. */
int sum_to(int n);

static void expect_eq(const char *name, int got, int want) {
    if (got == want) {
        printf("__T__|%s|PASS\n", name);
    } else {
        printf("__T__|%s|FAIL|expected %d but your code returned %d\n", name, want, got);
    }
}

int main(void) {
    expect_eq("sum_to(1) is 1", sum_to(1), 1);
    expect_eq("sum_to(5) is 15", sum_to(5), 15);
    expect_eq("sum_to(100) is 5050", sum_to(100), 5050);
    expect_eq("sum_to(0) is 0", sum_to(0), 0);
    return 0;
}
