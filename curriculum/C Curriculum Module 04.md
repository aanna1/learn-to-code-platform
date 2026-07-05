# Module 04 — Functions

> A function is a named block of code you can call by name — write the logic once, then reuse it as many times as you like.

You've been writing everything inside `main` so far. That works for tiny programs, but it gets messy fast. Functions let you give a chunk of work a name, hand it some inputs, and get a result back. Once you see how they fit together, your programs stop being one long wall of code and start reading like a list of steps.

## Prerequisites

- Modules 1–3 (you can write, run, and read a C program; you know types, operators, and control flow)

## What you'll learn

- The difference between *declaring* a function and *defining* it, and why C sometimes needs both
- How return types and parameters work, and how to write a `void` function that returns nothing
- The call-stack mental model: what actually happens when one function calls another
- How recursion works — a function that calls itself
- How `#include` connects you to library functions like the ones in `math.h`
- How a program reads command-line arguments with `argc` and `argv`

---

## What a function is

Think of a function like a recipe card. The card has a name ("make pancakes"), it lists what you need to hand it (flour, eggs, milk), and when you follow it you end up with something (pancakes). You don't rewrite the recipe every time you're hungry — you just say "make pancakes" again.

A C function is the same idea. Here's one that adds two numbers:

```c
#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int main(void) {
    int result = add(3, 4);
    printf("%d\n", result);
    return 0;
}
```

Press **Run** and you'll see:

```
7
```

Look at the first line of `add`. The `int` out front is the **return type** — `add` hands back an integer. The name is `add`. Inside the parentheses are the **parameters**: `int a` and `int b`, the two values the function expects. Inside the body, `return a + b;` sends a value back to whoever called it.

In `main`, the line `add(3, 4)` is the **call**. The `3` and `4` are the **arguments** — the actual values that get copied into `a` and `b`. Whatever `add` returns lands in `result`.

> **Watch out:** the arguments are *copied* into the parameters. If `add` changed `a` inside its body, the original value back in `main` wouldn't budge. C passes copies by default — this is called pass-by-value, and it's why you can't (yet) write a function that swaps two variables. We'll fix that in Module 6 with pointers.

---

## Declaring vs. defining

C reads your file top to bottom. When it reaches a function call, it wants to already know that function's shape — its name, what it returns, and what it takes. In the example above that worked because `add` was written *above* `main`. But what if you'd rather put `main` first?

Then you give C a heads-up with a **declaration** (also called a prototype): the function's signature followed by a semicolon, no body.

```c
#include <stdio.h>

int add(int a, int b);   // declaration — "this exists, here's its shape"

int main(void) {
    printf("%d\n", add(3, 4));
    return 0;
}

int add(int a, int b) {  // definition — the actual code
    return a + b;
}
```

This prints `7` too. The declaration is a promise: "a function called `add` takes two `int`s and returns an `int` — trust me, the body is coming later." The **definition** is the body that keeps the promise.

You'll see this split constantly once programs grow across multiple files. The declarations live in a header file you `#include`, and the definitions live in a `.c` file. That's exactly how `stdio.h` works — it declares `printf`, and the real `printf` code lives in the standard library.

> **Watch out:** if you call a function C hasn't seen declared or defined yet, the compiler complains (modern C treats it as an error, not a warning). If you get a message like "implicit declaration of function," you either called it before it was declared, or you forgot to `#include` the header that declares it.

---

## Functions that return nothing: `void`

Not every function hands a value back. Sometimes you just want it to *do* something — print a banner, draw a line. For those, the return type is `void`, which means "nothing comes back."

```c
#include <stdio.h>

void print_line(void) {
    printf("------------------------\n");
}

int main(void) {
    print_line();
    printf("Report\n");
    print_line();
    return 0;
}
```

Run it and you'll see:

```
------------------------
Report
------------------------
```

A `void` function has no `return value;` because there's nothing to return. You *can* write a bare `return;` to bail out early, but you'll often just let it run to the closing brace.

Notice `void` showing up in two spots and meaning two different things. As the *return type*, `void` means "returns nothing." Inside the *parentheses*, `void` means "takes no parameters" — that's why `main(void)` and `print_line(void)` both have it. Same keyword, two jobs.

---

## The call stack

When `main` calls `add`, where does the program "go," and how does it find its way back? The answer is the **call stack** — and it's worth a clear picture, because almost every confusing C bug later traces back to it.

Picture a stack of sticky notes. When a function is called, the program writes a fresh note for it: this note holds the function's parameters, its local variables, and a reminder of where to return when it's done. That note sits on *top* of the stack. When the function finishes, its note gets thrown away (popped off), and the one underneath — the caller — picks up exactly where it left off.

```c
#include <stdio.h>

int square(int n) {
    return n * n;
}

int sum_of_squares(int a, int b) {
    return square(a) + square(b);
}

int main(void) {
    printf("%d\n", sum_of_squares(2, 3));
    return 0;
}
```

This prints `13` (that's `4 + 9`). While `square(2)` is running, the stack has three notes: `main` at the bottom, then `sum_of_squares`, then `square` on top. The moment `square` returns `4`, its note is gone and we're back in `sum_of_squares`, which then calls `square(3)`. Each call gets its own private note, so the `n` inside one `square` call has nothing to do with the `n` in another.

> **Watch out:** each note takes up real space, and the stack isn't infinite. A function that calls itself forever (or just very deeply) keeps piling on notes until it runs out of room — a **stack overflow**, which crashes the program. That's the trap waiting in the next section.

---

## Recursion

A function is allowed to call itself. That sounds like a riddle, but it's just the call stack doing its normal thing — each call gets its own note, so the calls don't trip over each other.

The classic example is factorial. `5!` means `5 × 4 × 3 × 2 × 1`. Notice that `5!` is really `5 × 4!`, and `4!` is `4 × 3!`, and so on down to `1`. That "defined in terms of a smaller version of itself" shape is exactly what recursion expresses:

```c
#include <stdio.h>

int factorial(int n) {
    if (n <= 1) {       // base case: stop here
        return 1;
    }
    return n * factorial(n - 1);   // recursive case: shrink toward the base
}

int main(void) {
    printf("%d\n", factorial(5));
    return 0;
}
```

Run it and you get `120`.

Every recursive function needs two things. The **base case** is the version simple enough to answer without recursing — here, `factorial(1)` is just `1`. The **recursive case** does a little work and calls itself with a *smaller* input, marching toward that base case. Leave out the base case and you've written the infinite loop from the last warning: the stack fills up and the program crashes.

> **Watch out:** a missing or unreachable base case is the #1 recursion bug. If `factorial` called `factorial(n - 1)` with no `if`, it would run `factorial(0)`, `factorial(-1)`, `factorial(-2)`… forever, until a stack overflow. Always make sure each recursive call moves *toward* the base case, not away from it.

Recursion isn't always the right tool. A plain loop would compute factorial just fine, and usually faster. But for problems that are naturally self-similar, like walking a tree or exploring a maze, recursion reads beautifully. For now, just be comfortable with the mechanics.

---

## Borrowing functions: headers and `math.h`

You don't have to write every function yourself. The standard library ships with a pile of them, grouped into headers you `#include`. You've used `stdio.h` for `printf`. Another handy one is `math.h`, which gives you square roots, powers, rounding, and more.

```c
#include <stdio.h>
#include <math.h>

int main(void) {
    double root = sqrt(2.0);
    double power = pow(2.0, 10.0);
    printf("%f\n", root);
    printf("%f\n", power);
    return 0;
}
```

This prints:

```
1.414214
1024.000000
```

`sqrt` takes a `double` and returns its square root; `pow(base, exp)` raises `base` to the `exp`. Both come from `math.h`. Without that `#include`, the compiler wouldn't know what `sqrt` is.

> **Watch out:** the math functions work on `double`, not `int`. If you write `sqrt(2)` C will convert the `2` to `2.0` for you, but mixing up `int` and `double` types is a frequent source of surprising results — remember integer division from Module 2. When in doubt with math functions, use `double` values and the `%f` format specifier.

---

## Reading command-line arguments: `argc` and `argv`

Up to now `main` has looked like `int main(void)` — no inputs. But `main` can take two parameters that let your program receive input *before it even starts running*, supplied as command-line arguments:

```c
#include <stdio.h>

int main(int argc, char *argv[]) {
    printf("I got %d arguments\n", argc);
    for (int i = 0; i < argc; i++) {
        printf("  argv[%d] = %s\n", i, argv[i]);
    }
    return 0;
}
```

`argc` ("argument count") is how many arguments came in. `argv` ("argument vector") is the list of them, each one a string. Here in the course, you'll type arguments into the IDE's argument box and press **Run**. If you pass `red green blue`, you'll see:

```
I got 4 arguments
  argv[0] = ./program
  argv[1] = red
  argv[2] = green
  argv[3] = blue
```

Two things surprise people. First, `argc` is `4`, not `3`, because the program's own name is always `argv[0]` and the count includes it. Your real arguments start at `argv[1]`. Second, every argument is a **string**, even if you typed `42`. To do math with it, you'd convert it to a number first — `atoi("42")` turns the string `"42"` into the integer `42` (it lives in `stdlib.h`).

> **Watch out:** because `argv[0]` is the program name, looping from `0` will print or process the program name as if it were a real argument. When you want only the user's arguments, start your loop at `i = 1`. And never read `argv[5]` when only three arguments were passed — that's reading past the end of the list, which is undefined behavior.

---

## Try it: predict the output

```c
#include <stdio.h>

int mystery(int n) {
    if (n == 0) {
        return 0;
    }
    return n + mystery(n - 1);
}

int main(void) {
    printf("%d\n", mystery(4));
    return 0;
}
```

<details>
<summary>Predict the output, then click to check</summary>

```
10
```

`mystery` adds up every number from `n` down to `0`. The call unrolls like this: `mystery(4)` is `4 + mystery(3)`, which is `4 + 3 + mystery(2)`, and so on down to `mystery(0)`, which returns `0` and stops the recursion. So you get `4 + 3 + 2 + 1 + 0`, which is `10`. The base case (`n == 0`) is what keeps it from running forever.

</details>

---

## Recap

Functions are how you carve a program into named, reusable pieces. Each one has a return type, a set of parameters it copies its arguments into, and a body that can hand a value back with `return` (or nothing at all, if it's `void`). When you call a function, it gets its own slot on the call stack, runs, and hands control back to the caller when it returns — and that same machinery is what makes recursion work, as long as you give it a base case to stop at. You also saw that you don't have to build everything yourself: `#include` connects you to library functions like `sqrt` and `pow`, and `argc`/`argv` let `main` receive input from the command line. Next up, you'll put functions to work on real collections of data with arrays and strings.

---

## Quiz seeds

- Q: What's the difference between a function *declaration* and a function *definition*?
  - ✅ A declaration states the function's name, return type, and parameters (then a semicolon); a definition includes the actual body of code
  - ❌ A declaration has the body and a definition is just the signature — it's the other way around
  - ❌ They're two words for the same thing — C distinguishes them; the declaration is a promise, the definition fulfills it

- Q: A function is written as `void greet(void)`. What does the first `void` mean?
  - ✅ The function returns nothing — there's no value to hand back to the caller
  - ❌ The function takes no parameters — that's what the *second* `void` (inside the parentheses) means
  - ❌ The function can return any type — `void` means no return value, not "any type"

- Q: In `int main(int argc, char *argv[])`, you run the program with the arguments `cat dog`. What is `argc`?
  - ✅ 3 — the count includes the program's own name in `argv[0]`, plus `cat` and `dog`
  - ❌ 2 — that would be true if the program name weren't counted, but `argv[0]` is always the program name
  - ❌ 0 — `argc` is 0 only if even the program name is missing, which doesn't happen in normal runs

- Q: What happens if a recursive function has no reachable base case?
  - ✅ It calls itself forever, piling notes on the call stack until the program runs out of stack space and crashes (a stack overflow)
  - ❌ The compiler refuses to build it — C can't detect a missing base case at compile time; it crashes at runtime
  - ❌ It returns 0 automatically — there's no automatic stopping value; without a base case it never stops

---

## Checkpoint project

**Command-Line Calculator (browser).** Build a small calculator that reads its inputs as command-line arguments — two numbers and an operator — and prints the result. It's the first project where input arrives the way real command-line tools get it, and it pulls together everything from Modules 2–4: types and casting, branching on the operator, and now functions and `argc`/`argv`.

- Skills drilled: `argc`/`argv` (read through the IDE's argument input), converting argument strings to numbers, choosing a result type, branching on the operator with `if`/`else if` or `switch`, and splitting the arithmetic into small functions
- Done when: given arguments like `7 + 3`, the program prints `10`; it handles `+`, `-`, `*`, and `/`; it reports a clear message on malformed input (too few arguments, an unknown operator, or division by zero) instead of crashing
- Starter shape: a `main(int argc, char *argv[])` that checks `argc` is right, converts `argv[1]` and `argv[3]` to numbers, reads the operator from `argv[2]`, and dispatches to a small `add`/`subtract`/`multiply`/`divide` function — with hidden tests driving each operation and a few malformed inputs
