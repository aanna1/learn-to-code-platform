# Module 01 — The C Environment

> C is a compiled, statically typed language where you manage memory yourself — and in this course, the Run button handles the hard parts so you can focus on the language.

You already know Python. C is going to feel different in a few specific ways — and understanding *why* it's different is half the battle. Once you get the mental model, the syntax clicks fast. Let's write something that runs, and build the picture from there.

## Prerequisites

- Recommended: the Python course (or comfort with variables, loops, and functions in any language)

## What you'll learn

- How C differs from Python: compiled vs. interpreted, static typing, and manual memory management
- What the Run button actually does (preprocess → compile → link → run)
- How to read and write a first C program: `#include`, `main()`, `printf`, and `return 0`
- What the preprocessor does and why `#include` is its most common job

---

## How C is different from Python

Python runs your code line by line, as-is. You hand it a `.py` file, it reads it, and it goes. C doesn't work that way. Before your program can run, it has to be *compiled* — translated from source code into machine code that your computer executes directly. That translation step is what makes C programs fast.

There are two other differences that will affect almost everything you write:

**Static typing.** In Python, you can write `x = 5` and then `x = "hello"` and Python shrugs. In C, every variable has a fixed type declared upfront — `int x = 5;` — and it stays an `int` forever. The compiler checks your types before the program runs, which catches a whole class of bugs early.

**Manual memory.** Python manages memory for you — you create objects, and they disappear when nothing needs them anymore. In C, if you want memory beyond what's on the stack, you request it and you release it. That gives you fine-grained control, and it also means you can make mistakes Python would never let you make. We'll handle that carefully, step by step.

> **Watch out:** "Static typing" doesn't mean "slower to write." It means "the compiler knows the types at build time." Most bugs that would blow up at runtime in a dynamic language are caught as compile errors in C — before you ever press Run.

---

## What the Run button does

When you press **Run** in this course, four things happen in sequence:

1. **Preprocess** — the preprocessor scans for lines that start with `#` and acts on them. The most common one, `#include <stdio.h>`, tells it to paste in the contents of a standard header file. More on that below.
2. **Compile** — the compiler translates your source code into machine instructions and checks your types, syntax, and a lot more. This is where most errors surface.
3. **Link** — the linker combines your compiled code with any library code you used (like `printf`) into a single executable.
4. **Run** — the finished program executes and you see output in the terminal.

In a local C environment you'd do this manually: `gcc hello.c -o hello && ./hello`. Here, Run does all four steps in one click. The errors you see are real compiler errors — the same ones you'd see from `gcc` or `clang` on your own machine.

---

## Your first program

Here's the smallest complete C program:

```c
#include <stdio.h>

int main(void) {
    printf("Hello, world!\n");
    return 0;
}
```

Press **Run** and you'll see:

```
Hello, world!
```

Let's walk through each piece.

**`#include <stdio.h>`** — this is a preprocessor directive. It pulls in the *standard I/O* header, which gives you access to `printf` and other I/O functions. Without it, the compiler won't know what `printf` is.

**`int main(void)`** — every C program starts here. `main` is the entry point; the OS calls it when your program runs. `int` means `main` returns an integer. `void` in the parentheses means it takes no arguments (we'll add arguments in Module 4).

**`printf("Hello, world!\n")`** — prints text to the terminal. The `\n` is a newline character — without it, the cursor stays on the same line as your output. You'll use `printf` constantly.

**`return 0;`** — tells the OS "the program finished successfully." A non-zero return value signals an error. You can think of it as the program's exit code.

> **Watch out:** Every statement in C ends with a semicolon `;`. Forget one, and the compiler will usually complain about the *next* line — which looks confusing at first. If an error points somewhere that looks fine, check the line above for a missing `;`.

Try modifying the message and pressing Run again. C is very literal — it prints exactly what you tell it to.

---

## The preprocessor in brief

The preprocessor runs before the compiler sees your code. It handles any line that starts with `#`. Right now, the only directive you need is `#include`, which comes in two forms:

```c
#include <stdio.h>   // angle brackets: standard library header
#include "myfile.h"  // quotes: your own header file
```

Angle brackets tell the preprocessor to look in the system's standard include paths. Quotes tell it to look in your project directory first.

`stdio.h` ("standard input/output") is the header you'll include in almost every program this course. It gives you `printf` for output and `scanf` for input. We'll meet other standard headers as we need them — `math.h` for math functions, `string.h` for string operations, and more.

That's all you need to know about the preprocessor for now. We'll revisit it properly in Module 10 when we cover macros and header guards.

> **Watch out:** `#include` doesn't copy in a compiled library — it copies in *declarations* (function signatures). The actual `printf` code is in the C standard library, which the linker finds and connects for you. This distinction matters later; for now, just know that `#include` is what makes functions like `printf` available.

---

## Try it: predict the output

```c
#include <stdio.h>

int main(void) {
    int x = 10;
    int y = 3;
    printf("%d\n", x / y);
    return 0;
}
```

<details>
<summary>Predict the output, then click to check</summary>

```
3
```

In C, dividing two integers gives an integer — the fractional part is dropped, not rounded. `10 / 3` is `3`, not `3.333...`. This is called *integer division*, and it trips up nearly everyone who's used Python, where `10 / 3` gives `3.3333...`. In C, you'd write `10.0 / 3` (or cast one operand to `float`) to get the decimal result. We'll dig into this fully in Module 2.

</details>

---

## Recap

C gives you real control — over types, over memory, over performance — in exchange for more explicitness than Python. Every variable has a declared type. Every program compiles before it runs. Every `printf` needs a `\n` if you want a clean newline. That might feel like more ceremony at first, but it also means the compiler catches mistakes early, and what runs is exactly what you wrote.

The four-step pipeline (preprocess → compile → link → run) is what Run does for you here. In this course you'll focus on the language; the toolchain details come later in the Advanced Tracks, once you actually need them.

---

## Quiz seeds

- Q: What does `return 0;` at the end of `main` tell the operating system?
  - ✅ The program finished successfully (0 is the conventional success code)
  - ❌ The program returns the value 0 to `printf` — `printf` is a separate function; `main`'s return value goes to the OS, not to other functions in the program
  - ❌ It ends the loop — there's no loop here; `return` exits the function

- Q: Why does `#include <stdio.h>` appear at the top of almost every C program?
  - ✅ It makes `printf`, `scanf`, and other I/O functions available to your code
  - ❌ It starts the program — `main()` is the entry point, not `#include`
  - ❌ It compiles the code — `#include` is a preprocessor directive; compilation is a separate step

- Q: A classmate writes `int x = 5;` in C and then tries to write `x = "hello";` on the next line. What happens?
  - ✅ A compile error — `x` was declared as `int` and can't hold a string
  - ❌ `x` becomes the string "hello" — that's Python behavior; C variables have fixed types
  - ❌ The program crashes at runtime — the type error is caught at compile time, before the program runs
