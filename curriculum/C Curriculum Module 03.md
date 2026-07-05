# Module 03 — Control Flow

> Control flow is how your program makes decisions and repeats work. In C, a couple of small syntax traps can quietly change what your code does.

So far your programs have run top to bottom, one line after another. Real programs need to *choose* (do this if the number is even, that if it's odd) and *repeat* (keep asking until the input is valid). That's control flow. The ideas are the same ones you met in Python; the syntax is a little stricter, and there are two classic traps that catch nearly everyone. Let's meet both head-on.

## Prerequisites

- Module 02 (types, variables, and operators)

## What you'll learn

- How to branch with `if`, `else if`, and `else`
- How to use `switch` for multi-way choices — and why `break` matters inside it
- The three loops C gives you: `while`, `do-while`, and `for`
- How `break` and `continue` change a loop's behavior
- The two traps that bite every beginner: `=` vs `==`, and switch fallthrough

---

## if / else if / else

An `if` statement runs a block of code only when a condition is true. The condition goes in parentheses, and the code to run goes in curly braces.

```c
#include <stdio.h>

int main(void) {
    int temperature = 30;

    if (temperature > 25) {
        printf("It's warm out.\n");
    } else if (temperature > 10) {
        printf("Mild.\n");
    } else {
        printf("Bring a coat.\n");
    }

    return 0;
}
```

Press **Run** and you'll see:

```
It's warm out.
```

C checks each condition in order. The first one that's true wins, its block runs, and the rest are skipped. Here `temperature > 25` is true, so C prints `"It's warm out."` and never even looks at the `else if`. The `else` at the end is the catch-all. It runs only when every condition above it was false.

A condition in C is just a number. Zero means false; anything else means true. So `if (3)` always runs, and `if (0)` never does. There's no separate boolean type you have to use — though `<stdbool.h>` gives you `true` and `false` as nicer names if you want them.

> **Watch out:** the `=` vs `==` trap. `==` *compares* two values; a single `=` *assigns*. Writing `if (x = 5)` doesn't check whether `x` is 5; it sets `x` to 5, and since 5 is non-zero, the `if` always runs. The compiler usually warns you, but only if warnings are on. When you mean "is it equal to," always use `==`.

---

## switch (and fallthrough)

When you're checking one variable against a list of specific values, a long `else if` chain gets noisy. `switch` is the cleaner tool for that job. Think of it like a mailbox sorter: the value comes in, and it jumps straight to the matching slot.

```c
#include <stdio.h>

int main(void) {
    int day = 3;

    switch (day) {
        case 1:
            printf("Monday\n");
            break;
        case 2:
            printf("Tuesday\n");
            break;
        case 3:
            printf("Wednesday\n");
            break;
        default:
            printf("Some other day\n");
            break;
    }

    return 0;
}
```

Run it and you'll see:

```
Wednesday
```

C jumps to `case 3`, prints `"Wednesday"`, and then hits `break`, which exits the switch. The `default` case is the catch-all, like `else`: it runs when no `case` matches.

That `break` is doing real work. Without it, C keeps running straight into the next case's code — it does *not* stop at the next `case` label. This is called *fallthrough*, and it's the switch trap.

```c
#include <stdio.h>

int main(void) {
    int day = 1;

    switch (day) {
        case 1:
            printf("Monday\n");
        case 2:
            printf("Tuesday\n");
        default:
            printf("Done\n");
    }

    return 0;
}
```

This prints all three lines (`Monday`, `Tuesday`, `Done`) because with no `break`, execution falls from `case 1` straight through everything below it.

> **Watch out:** forgetting `break` is the most common `switch` bug. Each case should almost always end with `break`. Fallthrough is occasionally useful (letting several cases share one block), but if you do it on purpose, leave a comment so the next reader knows it wasn't a mistake.

---

## Loops: while, do-while, and for

A loop repeats a block of code. C gives you three, and they're suited to slightly different jobs.

A `while` loop checks its condition *before* each pass. If the condition is false the first time, the body never runs.

```c
#include <stdio.h>

int main(void) {
    int count = 1;

    while (count <= 3) {
        printf("count is %d\n", count);
        count++;
    }

    return 0;
}
```

Output:

```
count is 1
count is 2
count is 3
```

Each pass prints `count`, then `count++` adds one. Once `count` reaches 4, `count <= 3` is false and the loop stops.

A `do-while` loop is the same idea, but it checks the condition *after* the body — so the body always runs at least once. That's handy when you want to do something, then decide whether to repeat (like asking for input and re-asking if it was bad).

```c
#include <stdio.h>

int main(void) {
    int n = 10;

    do {
        printf("n is %d\n", n);
        n++;
    } while (n < 5);

    return 0;
}
```

This prints `n is 10` once and stops. The condition `n < 5` is false, but the body already ran before C checked it. Notice the semicolon after `while (...)` — a `do-while` needs it.

A `for` loop packs the three loop pieces (setup, condition, and update) onto one line. It's the natural choice when you're counting a known number of times.

```c
#include <stdio.h>

int main(void) {
    for (int i = 0; i < 5; i++) {
        printf("i = %d\n", i);
    }

    return 0;
}
```

Output:

```
i = 0
i = 1
i = 2
i = 3
i = 4
```

Read the header left to right: start `i` at 0; keep going while `i < 5`; after each pass, do `i++`. Starting at 0 and using `<` (not `<=`) runs the body exactly 5 times — the standard C counting pattern you'll write thousands of times.

> **Watch out:** the infinite loop. If a loop's condition never becomes false, it runs forever. The usual cause is forgetting to update the variable you're testing. Leave out `count++` in that first `while`, and `count` stays 1 forever. If your program seems to hang after you press Run, an unchanged loop variable is the first thing to check.

---

## break and continue

Sometimes you need to leave a loop early, or skip the rest of one pass. That's what `break` and `continue` are for.

`break` exits the loop immediately. It's the same keyword you saw in `switch`. Here it stops the search as soon as we find what we want:

```c
#include <stdio.h>

int main(void) {
    for (int i = 1; i <= 10; i++) {
        if (i == 4) {
            break;
        }
        printf("%d\n", i);
    }

    return 0;
}
```

This prints `1`, `2`, `3`, then `break` fires on `i == 4` and the loop ends — `4` and everything after it never print.

`continue` is gentler: it skips the rest of the current pass and jumps to the next one. Here we print only the odd numbers by skipping the evens:

```c
#include <stdio.h>

int main(void) {
    for (int i = 1; i <= 6; i++) {
        if (i % 2 == 0) {
            continue;
        }
        printf("%d\n", i);
    }

    return 0;
}
```

Output:

```
1
3
5
```

When `i` is even, `i % 2 == 0` is true, `continue` runs, and we jump past the `printf` to the next value of `i`. The odd values fall through to the print.

> **Watch out:** in a `while` loop, `continue` jumps back to the condition check; it does *not* run the update step for you. If your update (like `count++`) sits *after* a `continue`, it gets skipped, and you can spin into an infinite loop. In a `for` loop this isn't a problem, because the update is part of the loop header and always runs.

---

## Try it: predict the output

```c
#include <stdio.h>

int main(void) {
    int total = 0;

    for (int i = 1; i <= 5; i++) {
        if (i == 3) {
            continue;
        }
        total += i;
    }

    printf("%d\n", total);
    return 0;
}
```

<details>
<summary>Predict the output, then click to check</summary>

```
12
```

The loop adds 1, 2, 4, and 5 to `total` — it skips 3 because `continue` jumps past `total += i` on that pass. So `1 + 2 + 4 + 5 = 12`, not the `15` you'd get if every value were added.

</details>

---

## Recap

Control flow is how a program decides and repeats. Use `if` / `else if` / `else` for branching, and reach for `switch` when you're matching one value against a fixed list of cases — just remember the `break` at the end of each case, or you'll fall through. For repetition, pick the loop that fits: `while` checks first, `do-while` runs once then checks, and `for` is the counting workhorse. `break` leaves a loop early; `continue` skips to the next pass.

Two traps are worth burning into memory now, because they don't always announce themselves: `=` assigns while `==` compares, and a missing `break` in a `switch` falls through into the next case. Watch for those, keep an eye on your loop variables so they actually change, and your control flow will do exactly what you intended.

---

## Quiz seeds

- Q: What's the difference between `=` and `==` in a condition like `if (x == 5)`?
  - ✅ `==` compares two values; `=` assigns a value and would set `x` to 5, making the `if` always run
  - ❌ They're interchangeable in C — the compiler treats them the same inside an `if`
  - ❌ `=` compares and `==` assigns — it's the other way around
- Q: In a `switch`, what happens to a `case` that has no `break` at the end?
  - ✅ Execution falls through and keeps running the next case's code until it hits a `break` or the switch ends
  - ❌ C stops automatically at the next `case` label — `case` labels do not stop execution on their own
  - ❌ It causes a compile error — missing `break` is legal C, just usually a bug
- Q: Which loop is guaranteed to run its body at least once, even if the condition is false to begin with?
  - ✅ `do-while`, because it checks the condition after running the body
  - ❌ `while`, which checks the condition before the first pass and may run zero times
  - ❌ `for`, which checks its condition before the first pass and may run zero times
