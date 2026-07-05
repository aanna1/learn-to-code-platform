# C Curriculum — Master Spec

> Fill in the seed fields under each module, then run the **c-curriculum-builder** skill to
> expand them into `curriculum/C Curriculum Module NN.md`. Keep seeds terse — the skill writes
> the finished prose in the course voice. Schema: `reference/master-format.md`.

## Course meta
- Audience: complete beginners (recommended after the Python course)
- Runtime: browser (press Run) for all core modules; Advanced Tracks are local by design
- Voice: see `reference/voice-and-tone.md`

## Module list
| NN | Title | Checkpoint project | Track |
|----|-------|--------------------|-------|
| 01 | The C Environment | — | core |
| 02 | Types, Variables & Operators | — | core |
| 03 | Control Flow | — | core |
| 04 | Functions | Checkpoint A — Command-Line Calculator | core |
| 05 | Arrays & Strings | Checkpoint B — Tic-Tac-Toe (CLI) | core |
| 06 | Pointers | — | core |
| 07 | Dynamic Memory | — | core |
| 08 | Structs | Checkpoint C — Linked List from Scratch | core |
| 09 | File I/O | Checkpoint D — Student Grade Book | core |
| 10 | Standard Library, Scope, Preprocessor & Multi-File Builds | Checkpoint E — Word Frequency Counter | core |
| 11 | Debugging & Memory Tools | Capstone — Toy Memory Allocator | core |
| 12 | Advanced Track: Write a C Compiler (x86-64) | (the track itself) | advanced |
| 13 | Advanced Track: Build a Small OS | (the track itself) | advanced |

---

## Module 01 — The C Environment

### Description
<!-- one sentence -->

### Prerequisites
- (recommended) the Python course

### Learning objectives
- Explain compiled vs. interpreted, static typing, and manual memory at a high level
- Read a first program: `#include`, `main()`, `return 0`
- Understand what the Run button does (preprocess → compile → link → run)

### Concepts
- name: How C is different from Python
  seed:
  analogy:
  example:
  gotcha:
- name: Your first program
  seed:
  analogy:
  example:
  gotcha:
- name: The preprocessor in brief
  seed:
  analogy:
  example:
  gotcha:

### Predict-then-reveal seeds
- code:
  reveal:

### Quiz seeds
- q:
  correct:
  distractors:
    - ( ) — (why wrong)

---

## Module 02 — Types, Variables & Operators

### Description
### Prerequisites
- Module 01
### Learning objectives
- Use `int`, `float`, `double`, `char`; declare vs. initialize
- Read/format with `printf`/`scanf` and specifiers (`%d %f %c %s`)
- Use arithmetic, bitwise, and comparison operators; understand precedence; use `sizeof`
### Concepts
- name: Primitive types & sizeof
  seed:  analogy:  example:  gotcha:
- name: Declaring vs. initializing (uninitialized = UB)
  seed:  analogy:  example:  gotcha:
- name: Integer vs. floating-point arithmetic & casting
  seed:  analogy:  example:  gotcha:
- name: printf / scanf and format specifiers
  seed:  analogy:  example:  gotcha:
- name: Bitwise operators & precedence
  seed:  analogy:  example:  gotcha:
### Predict-then-reveal seeds
- code:  reveal:
### Quiz seeds
- q:  correct:  distractors:

---

## Module 03 — Control Flow

### Description
### Prerequisites
- Module 02
### Learning objectives
- Use `if`/`else if`/`else` and `switch`
- Use `while`, `do-while`, `for`; `break` and `continue`
- Avoid the `=` vs `==` and switch-fallthrough traps
### Concepts
- name: if / else if / else
  seed:  analogy:  example:  gotcha:
- name: switch (and fallthrough)
  seed:  analogy:  example:  gotcha:
- name: Loops (while / do-while / for)
  seed:  analogy:  example:  gotcha:
- name: break & continue
  seed:  analogy:  example:  gotcha:
### Predict-then-reveal seeds
- code:  reveal:
### Quiz seeds
- q:  correct:  distractors:

---

## Module 04 — Functions

### Description
### Prerequisites
- Module 03
### Learning objectives
- Declare vs. define functions; parameters and return types; `void`
- Build a mental model of the call stack; write a recursive function
- Use header files (`stdio.h`, `math.h`); read `argc`/`argv`
### Concepts
- name: Declaring & defining functions
  seed:  analogy:  example:  gotcha:
- name: The call stack
  seed:  analogy:  example:  gotcha:
- name: Recursion
  seed:  analogy:  example:  gotcha:
- name: Header files & includes
  seed:  analogy:  example:  gotcha:
- name: Command-line arguments (argc/argv)
  seed:  analogy:  example:  gotcha:
### Predict-then-reveal seeds
- code:  reveal:
### Quiz seeds
- q:  correct:  distractors:
### Checkpoint project
- name: Checkpoint A — Command-Line Calculator
- brief: parse args/input, convert strings to numbers, branch on the operator; tests check each
  operation and malformed input.

---

## Module 05 — Arrays & Strings

### Description
### Prerequisites
- Module 04
### Learning objectives
- Declare/index/iterate fixed-size arrays; use multi-dimensional arrays
- Understand C strings as `char[]` and the null terminator
- Use `string.h` (`strlen`, `strcpy`, `strncpy`, `strcmp`); spot buffer overruns
### Concepts
- name: Fixed-size arrays
  seed:  analogy:  example:  gotcha:
- name: Strings as char[] and the null terminator
  seed:  analogy:  example:  gotcha:
- name: string.h essentials
  seed:  analogy:  example:  gotcha:
- name: Multi-dimensional arrays
  seed:  analogy:  example:  gotcha:
- name: Buffer overruns (UB)
  seed:  analogy:  example:  gotcha:
### Predict-then-reveal seeds
- code:  reveal:
### Quiz seeds
- q:  correct:  distractors:
### Checkpoint project
- name: Checkpoint B — Tic-Tac-Toe (CLI)
- brief: 2D board, game loop, input validation, win/draw detection; tests drive scripted moves.

---

## Module 06 — Pointers

### Description
### Prerequisites
- Module 05
### Learning objectives
- Explain address vs. value; use `&` and `*`
- Pass by pointer vs. by value; understand `NULL` and array decay
- Recognize dangling pointers
### Concepts
- name: Address vs. value
  seed:  analogy:  example:  gotcha:
- name: & and *
  seed:  analogy:  example:  gotcha:
- name: Pass by pointer
  seed:  analogy:  example:  gotcha:
- name: Pointers and arrays (decay)
  seed:  analogy:  example:  gotcha:
- name: NULL and dangling pointers
  seed:  analogy:  example:  gotcha:
### Predict-then-reveal seeds
- code:  reveal:
### Quiz seeds
- q:  correct:  distractors:

---

## Module 07 — Dynamic Memory

### Description
### Prerequisites
- Module 06
### Learning objectives
- Use `malloc`, `calloc`, `realloc`, `free`
- Distinguish heap vs. stack
- Recognize leaks, double-free, and use-after-free
### Concepts
- name: malloc / calloc / realloc / free
  seed:  analogy:  example:  gotcha:
- name: Heap vs. stack
  seed:  analogy:  example:  gotcha:
- name: Leaks, double-free, use-after-free
  seed:  analogy:  example:  gotcha:
### Predict-then-reveal seeds
- code:  reveal:
### Quiz seeds
- q:  correct:  distractors:

---

## Module 08 — Structs

### Description
### Prerequisites
- Module 07
### Learning objectives
- Define structs, fields, initialization; arrays of structs
- Use pointers to structs (`->`) and `typedef`
- Meet `enum` and `union` briefly
### Concepts
- name: Defining structs
  seed:  analogy:  example:  gotcha:
- name: Arrays of structs
  seed:  analogy:  example:  gotcha:
- name: Pointers to structs (-> vs .)
  seed:  analogy:  example:  gotcha:
- name: typedef
  seed:  analogy:  example:  gotcha:
- name: enum & union (brief)
  seed:  analogy:  example:  gotcha:
### Predict-then-reveal seeds
- code:  reveal:
### Quiz seeds
- q:  correct:  distractors:
### Checkpoint project
- name: Checkpoint C — Linked List from Scratch
- brief: node struct, dynamic alloc, insert/delete/traverse, free the whole list; tests check
  structure and require a clean leak/UB pass.

---

## Module 09 — File I/O

### Description
### Prerequisites
- Module 08
### Learning objectives
- Use `fopen`/`fclose`, `fread`/`fwrite`, `fprintf`/`fscanf`, `fgets`
- Distinguish text vs. binary mode
- Handle errors with `errno` and `perror`
### Concepts
- name: Opening & closing files (virtual FS in the browser)
  seed:  analogy:  example:  gotcha:
- name: Reading & writing
  seed:  analogy:  example:  gotcha:
- name: Error handling (errno / perror)
  seed:  analogy:  example:  gotcha:
### Predict-then-reveal seeds
- code:  reveal:
### Quiz seeds
- q:  correct:  distractors:
### Checkpoint project
- name: Checkpoint D — Student Grade Book
- brief: structs + arrays of structs + CSV-style parsing + file persistence (virtual FS);
  tests check parsing, averages, lookups.

---

## Module 10 — Standard Library, Scope, Preprocessor & Multi-File Builds

### Description
### Prerequisites
- Module 09
### Learning objectives
- Use `stdlib.h`, `time.h`, `limits.h` essentials
- Understand scope/lifetime and `static`
- Use the preprocessor (`#define`, function-like macros, header guards) and reason about
  multi-file builds and linking
### Concepts
- name: Useful standard headers
  seed:  analogy:  example:  gotcha:
- name: Scope, lifetime, static
  seed:  analogy:  example:  gotcha:
- name: The preprocessor & macros
  seed:  analogy:  example:  gotcha:
- name: Declaration vs. definition across files (linking)
  seed:  analogy:  example:  gotcha:
### Predict-then-reveal seeds
- code:  reveal:
### Quiz seeds
- q:  correct:  distractors:
### Checkpoint project
- name: Checkpoint E — Word Frequency Counter
- brief: strings + dynamic memory + tally + sorting + file I/O; tests check counts, order, clean
  sanitizer pass.

---

## Module 11 — Debugging & Memory Tools

### Description
### Prerequisites
- Module 10
### Learning objectives
- Read compiler errors/warnings systematically
- Interpret a UBSan/AddressSanitizer report
- Understand the *concept* of gdb and valgrind (hands-on gdb lives in the Advanced Tracks)
- Odds & ends: `const` correctness and function pointers
### Concepts
- name: Reading compiler errors & warnings
  seed:  analogy:  example:  gotcha:
- name: Sanitizer reports (UBSan/ASan)
  seed:  analogy:  example:  gotcha:
- name: gdb & valgrind (concept)
  seed:  analogy:  example:  gotcha:
- name: const correctness & function pointers
  seed:  analogy:  example:  gotcha:
### Predict-then-reveal seeds
- code:  reveal:
### Quiz seeds
- q:  correct:  distractors:
### Checkpoint project
- name: Capstone — Toy Memory Allocator
- brief: implement malloc/free over a fixed buffer; the "you now understand the layer beneath
  you" project. Runs in-browser; pairs with the Advanced Tracks.

---

## Module 12 — Advanced Track: Write a C Compiler (x86-64)   [LOCAL]

### Description
Optional, post-course, local-environment track. Build a C compiler in C, targeting x86-64.
### Prerequisites
- Modules 01–11 + Track Onboarding (local toolchain, editor, gdb)
### Learning objectives
- Set up a real toolchain and editor; compile/run from the terminal
- Build lexer → parser → codegen across staged features (see docs/c-curriculum-map.md)
### Notes
- Framed as local by design. Teach the assembly each stage emits — it is NOT assumed from the
  core modules. Target x86-64 (not 32-bit).

---

## Module 13 — Advanced Track: Build a Small OS   [LOCAL]

### Description
Optional, post-course, local-environment track. Cross-compiler + QEMU, milestones 1–5.
### Prerequisites
- Modules 01–11 + Track Onboarding; comfort with Module 12 helps
### Learning objectives
- Set up an i686/x86_64-elf cross-compiler + QEMU
- Bootloader → VGA kernel → memory/paging → interrupts/keyboard → shell + multitasking skeleton
### Notes
- Document the ARM-Mac setup pain up front. Local by design.
