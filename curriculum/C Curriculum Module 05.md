# Module 05 — Arrays & Strings

> An array holds a whole row of values under one name, and a C string is just an array of characters with a special marker on the end.

So far every variable you've made has held exactly one thing — one number, one character. But programs usually deal with *collections*: a list of scores, the letters in a word, a grid of squares. Arrays are how C keeps many values of the same type together, and once you have arrays you basically already have strings, because in C a string is nothing more than an array of characters. Let's see how both work.

## Prerequisites

- Module 04 (you can write functions, pass arguments, and read `argc`/`argv`)
- Modules 1–3 (types, operators, and loops — you'll lean on `for` loops a lot here)

## What you'll learn

- How to declare, fill, and loop over a fixed-size array
- What a C string really is, and why the invisible `\0` on the end matters so much
- The handful of `string.h` functions you'll actually use: `strlen`, `strcpy`, `strncpy`, `strcmp`
- How a 2D array (a grid) works, which sets you up for the tic-tac-toe checkpoint
- What a buffer overrun is, why it's one of C's most famous footguns, and how to avoid it

---

## Fixed-size arrays

Think of an array as an egg carton. The carton has a fixed number of slots, all the same shape, sitting in a row. Each slot has a position number, and you reach any egg by its position. A C array is the same: a block of slots, all the same type, that you reach by an index.

Here's one holding five integers:

```c
#include <stdio.h>

int main(void) {
    int scores[5] = {90, 85, 100, 70, 95};

    printf("%d\n", scores[0]);
    printf("%d\n", scores[2]);
    return 0;
}
```

Press **Run** and you'll see:

```
90
100
```

A couple of things to notice. `int scores[5]` says "give me five `int` slots in a row, called `scores`." The values in the braces fill them in order. And the indexing starts at **0**, not 1 — so `scores[0]` is the first slot (the `90`) and `scores[2]` is the third (the `100`). That zero-based counting trips up almost everyone at first, so say it out loud a few times: the first element is at index 0.

Arrays really shine with a loop, because the index is just a number you can count up:

```c
#include <stdio.h>

int main(void) {
    int scores[5] = {90, 85, 100, 70, 95};
    int total = 0;

    for (int i = 0; i < 5; i++) {
        total += scores[i];
    }

    printf("total: %d\n", total);
    return 0;
}
```

Run it and you get `total: 440`. The loop walks `i` from 0 to 4, grabbing `scores[i]` each time and adding it up. That `i < 5` is doing important work — it stops the loop *before* index 5, because the last valid slot is index 4.

> **Watch out:** C does **not** check that your index is in range. Writing `scores[5]` or `scores[99]` won't get a polite error — it reads or writes memory that isn't yours, which is **undefined behavior**. The program might print garbage, might crash, might seem fine today and break tomorrow. Always keep your index between `0` and `length - 1`.

---

## Strings are arrays of characters

Here's the big reveal: C has no separate "string" type. A string is just an array of `char` with a special value, `\0` (the **null terminator**), marking where the text ends.

When you write a string in double quotes, C builds that array for you and adds the `\0` automatically:

```c
#include <stdio.h>

int main(void) {
    char name[] = "Sam";

    printf("%s\n", name);
    printf("%c\n", name[0]);
    return 0;
}
```

Run it and you see:

```
Sam
S
```

Even though you only typed three letters, `name` is actually **four** slots wide: `'S'`, `'a'`, `'m'`, and the hidden `'\0'`. That `\0` is how every string function knows where to stop. `printf` with `%s` starts at the front and keeps printing characters until it hits the `\0`. No terminator, no way to know where the string ends.

Picture it like a row of train cars with a "last car" sign on the caboose. The sign isn't cargo — you don't see it — but without it the conductor would keep walking off the end of the train.

> **Watch out:** if you ever build a string by hand, character by character, and forget to put the `\0` at the end, functions like `printf("%s")` and `strlen` will keep reading past your data into whatever happens to sit in memory next. That's a classic source of garbage output and crashes. The terminator isn't optional.

---

## string.h essentials

Because strings are just arrays, you can't copy or compare them with `=` and `==` the way you would a number. `name2 = name1` doesn't copy the letters, and `name1 == name2` compares *addresses*, not contents. Instead you use the helpers in `string.h`.

The four you'll reach for constantly:

```c
#include <stdio.h>
#include <string.h>

int main(void) {
    char greeting[20] = "Hello";

    printf("length: %zu\n", strlen(greeting));   // count the letters (not the \0)

    char copy[20];
    strcpy(copy, greeting);                       // copy greeting into copy
    printf("copy: %s\n", copy);

    if (strcmp(greeting, copy) == 0) {            // 0 means "equal"
        printf("they match\n");
    }
    return 0;
}
```

Run it:

```
length: 5
copy: Hello
they match
```

`strlen` counts the characters up to (but not including) the `\0` — so `"Hello"` is length 5. `strcpy(dest, src)` copies `src`'s characters, terminator and all, into `dest`. And `strcmp` returns `0` when two strings are equal, which reads a little backwards at first — remember it as "zero differences."

There's also `strncpy`, the safer cousin of `strcpy`. It takes a third argument capping how many characters it will copy, so it can't run off the end of a small destination:

```c
char small[5];
strncpy(small, "this is way too long", 4);
small[4] = '\0';   // strncpy may not add the terminator, so do it yourself
```

> **Watch out:** `strcpy` copies until it hits the source's `\0` and never checks whether the destination is big enough. Copying a 50-character string into a 10-slot array writes 40 characters past the end — a buffer overrun, and a real-world security bug. Make sure your destination is large enough, or use `strncpy` and set the terminator yourself.

---

## Multi-dimensional arrays

An array can hold rows of arrays, which gives you a grid. You declare it with two sizes — rows and columns — and index it with two numbers.

A tic-tac-toe board is exactly this: a 3-by-3 grid of characters.

```c
#include <stdio.h>

int main(void) {
    char board[3][3] = {
        {'X', 'O', 'X'},
        {' ', 'X', 'O'},
        {'O', ' ', 'X'}
    };

    for (int row = 0; row < 3; row++) {
        for (int col = 0; col < 3; col++) {
            printf("%c", board[row][col]);
        }
        printf("\n");
    }
    return 0;
}
```

Run it and the grid prints back out:

```
XOX
 XO
O X
```

`board[row][col]` picks one cell: the first index chooses the row, the second the column. The nested loops walk every cell — the outer loop steps down the rows, and for each row the inner loop sweeps across the columns. That row-then-column pattern is the workhorse for anything grid-shaped, and you'll use it directly in the checkpoint.

> **Watch out:** the same no-bounds-checking rule applies in both dimensions. `board[3][0]` is off the grid (valid rows are 0, 1, 2) and is undefined behavior, even though it *looks* like a reasonable fourth row.

---

## Buffer overruns

This deserves its own section, because it's the mistake C is most infamous for. A **buffer overrun** is when you read or write past the end of an array. C trusts you completely — it won't stop you — so the moment your index goes out of range, you're touching memory that belongs to something else.

Here's the bug in its simplest form:

```c
#include <stdio.h>

int main(void) {
    int nums[3] = {10, 20, 30};

    for (int i = 0; i <= 3; i++) {   // BUG: <= reaches index 3
        printf("%d\n", nums[i]);
    }
    return 0;
}
```

The array has slots 0, 1, and 2. But `i <= 3` lets the loop run one step too far and read `nums[3]`, which doesn't exist. What prints for that last line is anybody's guess — a leftover value, a zero, or a crash. The fix is the off-by-one you already know: use `i < 3`.

This is why the platform compiles your exercises with a **sanitizer** turned on. When your code steps out of bounds, the sanitizer catches it and fails the test loudly, instead of letting a silent bug slip through. Treat a sanitizer complaint as a real bug to fix, not noise.

> **Watch out:** the deadliest version of this bug is the one that *seems* to work. Reading one slot past the end often prints something plausible on your machine today and corrupts memory on someone else's tomorrow. "It ran fine for me" is not proof a C program is correct.

---

## Try it: predict the output

```c
#include <stdio.h>
#include <string.h>

int main(void) {
    char word[10] = "cat";
    word[3] = 's';

    printf("%s\n", word);
    printf("%zu\n", strlen(word));
    return 0;
}
```

<details>
<summary>Predict the output, then click to check</summary>

```
cats
4
```

`"cat"` is stored as `'c'`, `'a'`, `'t'`, `'\0'`. Overwriting index 3 (the `'\0'`) with `'s'` extends the visible word to `cats` — and it still prints correctly only because the array was 10 slots wide, so there's a leftover `'\0'` further along that stops `printf` and `strlen`. Length is now 4. If the array had been exactly `char word[4]`, that trick would have wiped out the terminator with no replacement, and you'd be reading off the end — a buffer overrun.

</details>

---

## Recap

An array is a fixed-size row of same-typed values you reach by a zero-based index, and a loop with the right `< length` bound is how you visit every element safely. C strings are just `char` arrays with a `\0` terminator on the end — that invisible marker is what every string function relies on to know where the text stops, so you copy and compare strings with `strcpy`/`strncpy` and `strcmp` rather than `=` and `==`. Stack two dimensions together and you get a grid you index with `[row][col]`, walked by nested loops. The thread running through all of it is that C never checks your indices for you: step past the end of an array and you've got a buffer overrun, which is undefined behavior and the single most important hazard to watch for as you start handling real collections of data.

---

## Quiz seeds

- Q: You declare `int scores[5];`. What is the index of the *last* valid element?
  - ✅ 4 — indexing starts at 0, so five slots are numbered 0 through 4
  - ❌ 5 — that's one past the end; reading `scores[5]` is a buffer overrun (undefined behavior)
  - ❌ 1 — arrays are zero-based, not one-based; index 1 is only the *second* element

- Q: How many `char` slots does the literal `"Sam"` actually occupy in memory?
  - ✅ 4 — the three letters plus the hidden `\0` null terminator on the end
  - ❌ 3 — that counts only the visible letters and forgets the terminator C adds automatically
  - ❌ 5 — there's no extra padding; it's exactly the letters plus one terminator

- Q: Two strings hold the same letters. What does `strcmp(a, b)` return?
  - ✅ 0 — `strcmp` returns 0 when the strings are equal ("zero differences")
  - ❌ 1 — a nonzero result means they *differ*; equal strings give 0
  - ❌ true — `strcmp` returns an `int`, and for equal strings that int is 0, which is actually "false"

- Q: Why is `strcpy(dest, src)` risky compared to `strncpy(dest, src, n)`?
  - ✅ `strcpy` copies until it hits the source's `\0` without checking that `dest` is big enough, so a too-long source overruns the destination
  - ❌ `strcpy` is slower — speed isn't the issue; the danger is writing past the end of `dest`
  - ❌ `strcpy` doesn't add a terminator — it does; it's `strncpy` that may *skip* the terminator if the limit is hit

---

## Checkpoint project

**Tic-Tac-Toe (CLI, browser).** Build a playable two-player tic-tac-toe game that runs right in the IDE. It's the first project with real state that changes over time — a board that updates move by move — and it pulls together everything from this module and the last two: a 2D array for the grid, loops to draw and scan it, and `if` logic to validate moves and detect a winner.

- Skills drilled: declaring and printing a `char[3][3]` board, a game loop that alternates players, reading and validating a move (in range, and the cell is empty), updating the board, and checking all rows, columns, and both diagonals for a win plus a full-board draw
- Done when: two players can alternate placing `X` and `O`; the program rejects out-of-range or already-taken moves instead of corrupting the board; and it correctly announces a win or a draw the moment one happens
- Starter shape: a `char board[3][3]` initialized to blanks, a `print_board` function, a `make_move` validator, and a `check_winner` that returns the winning mark or a sentinel for "no winner yet" — with hidden tests driving scripted move sequences and asserting the board state and the announced result
