# Module 06 — Pointers

> A pointer is a variable that holds the *address* of another variable — a way to say "the value you want lives over there" instead of holding the value itself.

Here's the thing Python kept hidden from you: every variable lives at a numbered spot in memory, and you can hold onto that number. That number is an address, and a pointer is just a variable that stores one. Pointers have a scary reputation, but the core idea is small. Once it clicks, a lot of C that looked like magic — how a function changes your variable, why arrays and strings behave the way they do — turns into plain sense.

## Prerequisites

- Modules 1–5 (you can write and run a C program; you know types, functions, and arrays)

## What you'll learn

- The difference between a value and the *address* where it lives
- How to take an address with `&` and follow it with `*`
- How to write a function that actually changes your variable, using pass-by-pointer
- Why an array's name is so closely tied to a pointer ("array decay")
- What `NULL` is for, and how a dangling pointer goes wrong

---

## Address vs. value

Picture memory as a very long street of houses, each with a number on the front. When you write `int age = 30;`, C parks the value `30` in one of those houses and lets you call it `age`. Most of the time you only care about the value — the `30`. But the house also has an *address*, and that address is a thing you can talk about, write down, and hand to someone else.

That's the whole split. A variable has a **value** (what's inside the house) and an **address** (which house it is). Up to now you've only used values. Pointers are how you work with addresses.

```c
#include <stdio.h>

int main(void) {
    int age = 30;
    printf("value:   %d\n", age);
    printf("address: %p\n", (void *)&age);
    return 0;
}
```

Press **Run**. The first line prints `value: 30`. The second prints something like `address: 0x7ffe...` — a long hexadecimal number. That's the house number where `age` lives. You'll get a different address each run, and that's fine; you almost never care what the number *is*, only that you can grab it.

> **Watch out:** `%p` is the format specifier for an address, and it expects a `void *`, which is why we wrote `(void *)&age`. Print an address with `%d` instead and the output is meaningless (and the compiler will warn you). Match the specifier to the thing you're printing.

---

## Taking an address with `&`, following it with `*`

Two operators do all the work, and they're opposites of each other.

The `&` operator means **"address of."** Stick it in front of a variable and you get its house number. You've actually seen `&` already — back in `scanf("%d", &age)`, that `&` handed `scanf` the *address* of `age` so it could write into it.

The `*` operator, when you use it on a pointer, means **"the value at this address"** — it *follows* the pointer to the house and reads what's inside. This is called **dereferencing**.

```c
#include <stdio.h>

int main(void) {
    int age = 30;
    int *p = &age;     // p holds the address of age

    printf("%d\n", *p);   // follow p, read the value: 30

    *p = 31;              // follow p, write a new value
    printf("%d\n", age);  // age itself changed: 31
    return 0;
}
```

Run it and you'll see `30` then `31`. Read `int *p = &age;` as "`p` is a pointer to an `int`, and it starts out pointing at `age`." The `*` in that *declaration* is part of the type — it says "this is a pointer." The `*` in `*p` later is the *action* — "go follow it." Same symbol, two jobs, just like `void` had two jobs back in Module 4.

The payoff is the line `*p = 31;`. We never mentioned `age` there, but `age` changed to `31` — because `p` pointed at it, and writing through the pointer writes into the house it points to. The pointer is a second name for the same box.

> **Watch out:** the type has to match. A pointer to an `int` is `int *`; a pointer to a `double` is `double *`. You can't point an `int *` at a `double` and expect sane results — the pointer's type tells C how many bytes to read and how to interpret them when you dereference.

---

## Pass by pointer

Remember the promise from Module 4: C passes arguments *by value*, meaning the function gets a copy. That's why you couldn't write a function that swaps two variables — it would only swap its own copies, and the originals back in `main` wouldn't budge. Here's the broken version:

```c
#include <stdio.h>

void swap(int a, int b) {   // a and b are COPIES
    int temp = a;
    a = b;
    b = temp;
}

int main(void) {
    int x = 1, y = 2;
    swap(x, y);
    printf("%d %d\n", x, y);   // still 1 2 — nothing changed
    return 0;
}
```

Run it: you get `1 2`. The swap happened, but only to `a` and `b`, which vanished when `swap` returned.

Now hand the function the *addresses* instead. If `swap` knows where `x` and `y` live, it can reach back and change them directly:

```c
#include <stdio.h>

void swap(int *a, int *b) {   // a and b are addresses
    int temp = *a;            // read the value at a
    *a = *b;                  // write b's value into a's house
    *b = temp;
}

int main(void) {
    int x = 1, y = 2;
    swap(&x, &y);             // hand over the addresses
    printf("%d %d\n", x, y);  // 2 1 — they really swapped
    return 0;
}
```

This prints `2 1`. The function still gets copies — but now the copies are *copies of the addresses*, and an address is enough to find the original and write into it. This pattern, **pass-by-pointer**, is how a C function changes something owned by its caller. It's also how `scanf` writes your input back into your variables.

> **Watch out:** inside `swap` you must dereference. Write `a = b;` (no `*`) and you've only swapped the local address copies, changing nothing back in `main` — and the compiler may not warn you, because swapping two pointers is itself a legal thing to do. The `*` is what reaches through to the real value.

---

## Pointers and arrays: "decay"

Arrays and pointers are close cousins in C, and here's the link. When you use an array's name in most expressions, it quietly turns into a pointer to its first element. People call this **array decay**. It's why an array name can be passed to a function that expects a pointer.

```c
#include <stdio.h>

int main(void) {
    int nums[3] = {10, 20, 30};
    int *p = nums;        // no & needed: the name decays to &nums[0]

    printf("%d\n", *p);       // 10  — first element
    printf("%d\n", *(p + 1)); // 20  — next element over
    printf("%d\n", nums[2]);  // 30  — normal indexing still works
    return 0;
}
```

Run it: `10`, `20`, `30`. Notice you didn't write `&nums` — the bare name `nums` already *is* the address of the first element. And `*(p + 1)` reaches the next element, because adding `1` to a pointer doesn't add one byte, it moves forward by one *element* (one whole `int`). That's **pointer arithmetic**, and it's exactly what `nums[1]` does under the hood — `nums[i]` is shorthand for `*(nums + i)`.

> **Watch out:** decay loses the size. Inside a function that takes `int *p`, `sizeof(p)` is the size of a *pointer* (often 8 bytes), not the size of the whole array — the length didn't come along for the ride. That's why functions in Module 5 always took the length as a separate parameter. The array forgot how long it was the moment it decayed.

---

## `NULL` and dangling pointers

A pointer has to point *somewhere*, but sometimes you want one that deliberately points at nothing yet — a placeholder. That's `NULL`: a special address value meaning "this points to nothing." It comes from `stdio.h` (and others), and you check for it before following a pointer.

```c
#include <stdio.h>

int main(void) {
    int *p = NULL;        // points at nothing, on purpose

    if (p == NULL) {
        printf("p isn't pointing anywhere yet\n");
    } else {
        printf("value is %d\n", *p);
    }
    return 0;
}
```

This prints `p isn't pointing anywhere yet`. The guard matters: dereferencing a `NULL` pointer with `*p` crashes the program. Checking `if (p != NULL)` before you follow a pointer is one of the most common safety habits in C.

The other hazard is a **dangling pointer** — a pointer that still holds an address, but the thing that lived there is gone. The classic mistake is returning the address of a local variable:

```c
#include <stdio.h>

int *broken(void) {
    int local = 42;
    return &local;   // BAD: local dies when broken() returns
}

int main(void) {
    int *p = broken();
    printf("%d\n", *p);   // following a pointer to a house that's been demolished
    return 0;
}
```

`local` lives on the call stack — remember the sticky-note picture from Module 4. The moment `broken` returns, its note is thrown away and `local`'s house is up for grabs. The address `p` holds is now pointing at demolished ground. Reading through it is **undefined behavior**: maybe you get `42`, maybe garbage, maybe a crash. It's a bug even when it seems to "work."

> **Watch out:** a dangling pointer is one of C's nastiest traps because the program can appear fine in testing and break later. Two rules keep you safe for now: never return the address of a local variable, and set a pointer to `NULL` once whatever it pointed at is gone, so a stray dereference fails loudly instead of silently reading garbage. In Module 7 you'll meet `malloc`, which gives you memory that *doesn't* vanish when a function returns — the proper fix for "I need this to outlive the function."

---

## Try it: predict the output

```c
#include <stdio.h>

void add_ten(int *n) {
    *n = *n + 10;
}

int main(void) {
    int score = 5;
    int *p = &score;

    add_ten(p);
    add_ten(&score);

    printf("%d\n", *p);
    return 0;
}
```

<details>
<summary>Predict the output, then click to check</summary>

```
25
```

Both `p` and `&score` are the same address — they both point at `score`. The first `add_ten(p)` follows the pointer and bumps `score` from `5` to `15`. The second `add_ten(&score)` does it again, `15` to `25`. Then `*p` follows the pointer one more time and reads `25`. The lesson: there's only ever one `score`, and every pointer to it is just another door into the same house.

</details>

---

## Recap

A pointer holds an address — the location of a value rather than the value itself. You take an address with `&` and follow it with `*`, and writing through a pointer changes the original variable, because the pointer is a second name for the same box. That's what makes pass-by-pointer work: hand a function the addresses of your variables and it can reach back and change them, which is exactly how `scanf` and a working `swap` operate. Array names decay into pointers to their first element, so indexing and pointer arithmetic are two ways of saying the same thing — though decay drops the length, which is why you keep passing it around. And two pointers will bite you if you're careless: a `NULL` pointer points at nothing (guard before you follow it), and a dangling pointer points at something that's already gone (never return the address of a local). Next module you'll ask the system for memory that sticks around on purpose, with `malloc` and friends.

---

## Quiz seeds

- Q: What does the `&` operator do in `int *p = &age;`?
  - ✅ It gives the *address* of `age` — the location in memory where `age` is stored — and stores it in `p`
  - ❌ It gives the *value* of `age` — that's just `age` by itself; `&` is specifically "address of"
  - ❌ It declares `p` as a pointer — the `*` in `int *p` does that; `&` is the address-of operator on the right-hand side

- Q: Inside `void swap(int *a, int *b)`, why does `*a = *b;` change the caller's variable but `a = b;` would not?
  - ✅ `*a = *b` writes through the pointer into the original variable's memory; `a = b` only reassigns the local copy of the address, leaving the originals untouched
  - ❌ There's no difference — both swap the caller's values; C figures out what you meant
  - ❌ `a = b` is a syntax error in C, so only `*a = *b` compiles — actually `a = b` compiles fine (it copies the pointer), which is exactly why the bug is sneaky

- Q: A function does `int local = 42; return &local;`. What's wrong with returning that address?
  - ✅ `local` lives on the stack and is destroyed when the function returns, so the returned pointer dangles — it points at memory that's no longer valid (undefined behavior to use)
  - ❌ Nothing — the caller safely gets `42` every time; in fact the value is unreliable because `local`'s storage is reclaimed when the function returns
  - ❌ You can't return a pointer from a function in C — you can; the problem is specifically that it points at a *local* that has gone away

- Q: After `int nums[3] = {10, 20, 30};`, what is `*(nums + 1)`?
  - ✅ `20` — `nums` decays to a pointer to the first element, and `+ 1` moves forward one whole `int`, so this is the same as `nums[1]`
  - ❌ `11` — pointer arithmetic moves by *elements*, not by single bytes, so `+ 1` advances one `int`, not one byte
  - ❌ The address of the second element — the surrounding `*` dereferences that address, giving the value `20`, not the address
