# Module 07 — Dynamic Memory

> Dynamic memory lets your program ask for storage while it's running and hand it back when it's done — so the size of your data no longer has to be decided in advance.

Up to now every array you've made had a fixed size, baked in when you wrote the code. But real programs often don't know how much they'll need until they're already running — how many lines a user will type, how many records a file holds. Dynamic memory is how C lets you ask for exactly as much room as you need, right when you need it. It's powerful, and it comes with a catch: what you borrow, you have to give back.

## Prerequisites

- Modules 1–6 (you can write and run C, and you're comfortable with pointers, `&`, `*`, and `NULL`)

## What you'll learn

- The difference between the **stack** and the **heap**, and why dynamic memory lives on the heap
- How to ask for memory with `malloc` and `calloc`, and how to read what they hand back
- How to grow a block you already have with `realloc`
- How to give memory back with `free`, and why forgetting to is a **memory leak**
- The two classic hazards that come with `free`: the **double-free** and the **use-after-free**

---

## Two places memory comes from: the stack and the heap

Every variable you've made so far has lived on the **stack**. When a function is called, it gets a little slab of memory for its local variables, and when the function returns, that slab is automatically thrown away. It's tidy and fast, and you never have to think about cleanup. The catch is that the stack is for things whose size and lifetime the compiler can figure out ahead of time.

The **heap** is the other pool. Think of the stack as a stack of trays in a cafeteria: you take the top one, you put it back, it's automatic and orderly. The heap is more like a big storage warehouse. You walk up to the desk, ask for a space of a certain size, and they hand you a locker key. That space is yours until *you* go back and return the key. Nobody cleans it up for you.

That trade is the whole point of this module. The heap lets you decide sizes at runtime and keep data alive past the function that created it. In exchange, you're now the one responsible for handing it back.

> **Watch out:** never return a pointer to a local (stack) variable from a function. The moment the function returns, that variable's slab is gone, and the pointer now points at memory that's been reclaimed. Heap memory is exactly the tool for "I need this to outlive the function that made it."

## Asking for memory: `malloc`

`malloc` ("memory allocate") is how you ask the heap for a block. You tell it how many bytes you want, and it hands back a pointer to the start of that block, or `NULL` if it couldn't find the room.

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *p = malloc(sizeof(int));   // ask for room for one int
    if (p == NULL) {                // always check!
        printf("Out of memory\n");
        return 1;
    }

    *p = 42;                        // use it like any other pointer
    printf("%d\n", *p);

    free(p);                        // give it back when done
    return 0;
}
```

Press **Run** and you'll see:

```
42
```

A few things to notice. `sizeof(int)` asks for exactly the number of bytes one `int` needs, so your code stays correct no matter the platform. `malloc` is declared in `<stdlib.h>`, so that header has to be included. And the value comes back as a pointer, which is why `p` is an `int *` and we use `*p` to read and write the actual integer.

> **Watch out:** always check whether `malloc` returned `NULL` before you use the pointer. If memory ran out and you skip the check, `*p = 42` writes through a null pointer, an instant crash. The `if (p == NULL)` guard is not optional politeness; it's how you avoid undefined behavior.

## Asking for many: `malloc` for arrays

The real power shows up when you want an array whose size you only learn at runtime. You ask for `n` elements' worth of bytes in one go.

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int n = 5;
    int *nums = malloc(n * sizeof(int));   // room for 5 ints
    if (nums == NULL) {
        return 1;
    }

    for (int i = 0; i < n; i++) {
        nums[i] = i * 10;                  // index it like a normal array
    }

    for (int i = 0; i < n; i++) {
        printf("%d ", nums[i]);
    }
    printf("\n");

    free(nums);
    return 0;
}
```

Press **Run** and you'll see:

```
0 10 20 30 40
```

Notice you index `nums` with `nums[i]` exactly like a regular array. That's the array-decay idea from Module 6 working for you: a pointer to the first element behaves like an array. The difference is that `n` could have come from the user, a file, or a calculation, so the size wasn't frozen when you wrote the code.

> **Watch out:** `malloc` does **not** clear the memory it gives you. The bytes hold whatever junk was there before. Reading `nums[i]` before you've written to it is undefined behavior: the same uninitialized-variable hazard from Module 2, now on the heap.

## Asking for *clean* memory: `calloc`

If you'd rather get memory that's already zeroed, use `calloc`. It takes two arguments (the number of elements and the size of each) and sets every byte to zero before handing the block back.

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int n = 4;
    int *nums = calloc(n, sizeof(int));   // n elements, each sizeof(int), all zero
    if (nums == NULL) {
        return 1;
    }

    for (int i = 0; i < n; i++) {
        printf("%d ", nums[i]);           // already zero — we never wrote these
    }
    printf("\n");

    free(nums);
    return 0;
}
```

Press **Run** and you'll see:

```
0 0 0 0
```

So the choice is simple. Reach for `calloc` when you want a clean, zeroed start (a counter array, say). Reach for `malloc` when you're going to fill every slot yourself anyway and don't need the zeroing.

## Growing a block: `realloc`

Sometimes you ask for room, start filling it, and realize you need more. `realloc` takes a block you already have and resizes it. It returns a pointer to the resized block, which might be in a brand-new location, with your old contents copied over for you.

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *nums = malloc(2 * sizeof(int));
    if (nums == NULL) return 1;
    nums[0] = 1;
    nums[1] = 2;

    int *bigger = realloc(nums, 4 * sizeof(int));   // grow to 4 ints
    if (bigger == NULL) {
        free(nums);                                 // old block still valid on failure
        return 1;
    }
    nums = bigger;                                  // adopt the new pointer

    nums[2] = 3;
    nums[3] = 4;

    for (int i = 0; i < 4; i++) {
        printf("%d ", nums[i]);
    }
    printf("\n");

    free(nums);
    return 0;
}
```

Press **Run** and you'll see:

```
1 2 3 4
```

The careful dance here is worth copying. We catch the result in a *new* pointer, `bigger`, instead of overwriting `nums` directly. Why? Because if `realloc` fails it returns `NULL` but leaves the old block untouched, and if you'd already stomped `nums` with that `NULL`, you'd have lost your only handle to the memory and leaked it. Check first, then adopt.

> **Watch out:** after a successful `realloc`, the *old* pointer may no longer be valid, because the block can move. Use only the pointer `realloc` returned from then on. Touching the old one is a use-after-free in disguise.

## Giving it back: `free` and what goes wrong

Every successful `malloc`, `calloc`, or `realloc` should be matched by exactly one `free`. Miss it, and you have a **memory leak**: the block stays reserved, unusable, until the program ends. One leaked block is harmless; a leak inside a loop that runs for hours will slowly eat all the memory the program can get.

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    for (int i = 0; i < 3; i++) {
        int *p = malloc(sizeof(int));   // allocate inside the loop...
        *p = i;
        printf("%d\n", *p);
        // ...and never free it — a leak on every iteration
    }
    return 0;
}
```

Press **Run** and the output looks fine:

```
0
1
2
```

That's the trap: a leak doesn't show up in your output. In the browser the run is compiled with a leak detector, so after the program ends you'll see a report calling out the bytes that were allocated and never freed. Listen to it. The fix is one line: `free(p);` at the end of each iteration, before `p` is reassigned.

Two more hazards come from misusing `free` itself. Naming them is half the battle:

A **double-free** is calling `free` on the same block twice. After the first `free`, that block is no longer yours; freeing it again corrupts the heap's bookkeeping and is undefined behavior.

A **use-after-free** is reading or writing through a pointer *after* you've freed it. The locker's been returned, but you kept a copy of the key and walked back in — whatever's in there now isn't yours.

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *p = malloc(sizeof(int));
    *p = 7;
    free(p);            // p's memory is returned here

    printf("%d\n", *p); // USE-AFTER-FREE: reading freed memory — undefined behavior
    free(p);            // DOUBLE-FREE: freeing the same block again — undefined behavior
    return 0;
}
```

This program might print `7`, might print garbage, might crash. That's what "undefined" means. A simple habit kills both bugs at once: right after you `free` a pointer, set it to `NULL`. A freed-then-nulled pointer can't be used by accident (deref'ing `NULL` crashes loudly instead of silently corrupting), and `free(NULL)` is explicitly defined to do nothing, so a stray second free is harmless.

> **Watch out:** `free(p); p = NULL;` is one of the most valuable two-line habits in C. It turns two of the nastiest, hardest-to-reproduce bugs in the language into either a clean no-op or an obvious, immediate crash.

## Try it: predict the output

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *a = calloc(3, sizeof(int));
    a[1] = 5;

    int *b = realloc(a, 5 * sizeof(int));
    b[3] = 9;

    printf("%d %d %d %d\n", b[0], b[1], b[3], b[4]);

    free(b);
    return 0;
}
```

<details>
<summary>Predict the output, then click to check</summary>

```
0 5 9 0
```

`calloc` zeroed the first three slots, so `b[0]` is still `0` and `b[1]` is the `5` we stored, which `realloc` copied over. We set `b[3]` to `9`. But `b[4]` is the tricky one: `realloc` zeroes nothing, so the *new* slots it adds hold uninitialized junk. It prints `0` here only by luck of this run — reading `b[4]` before writing it is undefined behavior, and you shouldn't rely on it.

</details>

## Recap

The heap is the pool of memory you manage by hand, and it's what lets your program decide sizes and lifetimes while it's running instead of at compile time. You ask for a block with `malloc` (raw bytes) or `calloc` (zeroed), grow one with `realloc`, and you read what comes back as a pointer, always checking for `NULL` first. The deal is that every block you take, you give back with exactly one `free`. Skip the `free` and you leak; `free` twice and you've got a double-free; touch a pointer after freeing and it's a use-after-free. The single habit of writing `free(p); p = NULL;` defends against the last two, and the browser's leak detector will catch the first. Next, you'll use these tools to build a data structure that grows one node at a time: the linked list.

---

## Quiz seeds

- Q: What does `malloc` return if it cannot find enough memory?
  - ✅ `NULL` — which is why you must check the pointer before using it
  - ❌ `0` bytes of usable memory but a valid pointer — there's no valid pointer to a failed allocation; it returns `NULL`
  - ❌ It crashes the program automatically — `malloc` doesn't crash; it reports failure by returning `NULL`, and *you* crash if you don't check

- Q: What's the difference between `malloc` and `calloc`?
  - ✅ `calloc` zeroes the memory before returning it (and takes count and size separately); `malloc` leaves the bytes uninitialized
  - ❌ `malloc` is for arrays and `calloc` is for single values — both can do either; the real difference is zeroing
  - ❌ `calloc` doesn't need to be freed — both must be freed exactly once; how you allocate doesn't change that

- Q: You write `free(p);` and later, by mistake, `free(p);` again. What is this bug called, and what simple habit prevents it?
  - ✅ A double-free; setting `p = NULL` right after the first `free` prevents it, since `free(NULL)` does nothing
  - ❌ A memory leak; you prevent it by freeing twice — a leak is forgetting to free, and freeing twice is itself the bug, not a fix
  - ❌ A use-after-free; it's harmless and needs no fix — it's a double-free, and it corrupts the heap (undefined behavior), so it does need fixing

- Q: After a successful `realloc`, why should you stop using the original pointer?
  - ✅ `realloc` may move the block to a new address, so only the returned pointer is guaranteed valid
  - ❌ The original pointer is always still valid — `realloc` never moves data — it can and does move the block, which is exactly why it returns a pointer
  - ❌ You should free the original pointer first, then realloc — `realloc` handles the old block itself; freeing it yourself would be a double-free

---

## Checkpoint project

**Linked List from Scratch (browser).** Build the data structure that's a rite of passage for every C programmer: a singly linked list. Each node is a `struct` holding a value and a pointer to the next node, allocated on the heap with `malloc`. You'll write the operations that insert nodes, traverse the list to print it, delete nodes, and — the part that really tests you — `free` every node so the whole thing leaves no leak behind. It pulls together pointers from Module 6 and everything about dynamic memory here.

- Skills drilled: defining a `struct` node with a self-referential `next` pointer, `malloc`-ing nodes, linking them by pointer, traversing with a walking pointer, deleting a node by relinking around it, and freeing the entire list without leaking or double-freeing
- Done when: you can insert several values, print the list in order, delete a value, and free the whole list — with the hidden tests checking structural correctness *and* the sanitizer/leak report coming back completely clean
- Starter shape: a `typedef struct Node { int value; struct Node *next; } Node;`, plus `Node *insert(Node *head, int value)`, a `void print_list(Node *head)`, a `Node *delete_value(Node *head, int value)`, and a `void free_list(Node *head)` — with hidden tests driving scripted insert/delete sequences and asserting both the resulting values and a leak-free run
