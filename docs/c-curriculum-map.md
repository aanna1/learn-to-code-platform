# C Language Curriculum — Revised Map (v2)

**Status:** Draft for review. Supersedes the first C map.
**Core decision:** Every unit and every checkpoint project runs **in the browser**, inside
the existing `<Ide>` (same Run/Submit/hidden-test/friendly-error machinery as the Python
build). The **only** local-environment work is the two optional advanced tracks at the very
end — the Compiler and the OS — which are intentionally done on the learner's own machine so
that graduates get real toolchain, editor, and setup experience after they already know C.

---

## Why the split (rationale to keep front-of-mind)

The platform's whole value for beginners is "no install, runs in the browser, instant
graded feedback." Beginners learning C *and* a toolchain *and* an editor at once is the
biggest attrition risk, so the entire teaching path stays in-browser. The Compiler and OS
are genuinely expert projects; by the time a learner reaches them they've finished the
course, so handing them a real local environment is a feature, not a barrier — it's the
"graduate to the real world" capstone. Keeping them local also sidesteps the things the
browser runtime can't do anyway (emitting/assembling x86, cross-compiling, QEMU, bare metal).

---

## Architecture / integration notes (so this fits the existing site)

- **Reuse the `Language` interface.** C registers like Python: `config`, `runtime`,
  `linter`, `errorExplainer`. Components never branch on `language === "c"`.
- **In-browser C runtime.** Needs a WASM-based C compile-and-run path (investigate a WASM
  build of a C toolchain / a clang-in-WASM approach) feeding stdout/stderr back to the
  xterm terminal, exactly like the Pyodide worker streams Python output. `input()`'s C
  analogue is `scanf`/`fgets` reading from the same SAB-blocked stdin channel already built
  for Python's `input()`.
- **Grading = compile + run + test, ideally with a sanitizer.** Port the `test_*`
  convention conceptually: a hidden `tests.c` (or a test harness `main`) that calls the
  learner's functions and asserts. Where feasible, compile exercises with
  `-fsanitize=address,undefined` so leaks / UB / out-of-bounds **fail the test** instead of
  silently "passing." This is the single biggest reason to keep C in the browser — it gives
  C the automated-feedback loop it needs even more than Python does.
- **Linter.** Reuse the diagnostics pipeline; surface compiler warnings (`-Wall -Wextra`) as
  Monaco markers the way Ruff findings are mapped today.
- **Editor.** Default editor for all units = the in-browser Monaco IDE. Vim/local tooling is
  taught **only** in the Advanced Tracks (see below), never as a prerequisite to learn C.

---

## Prerequisites (state these explicitly on the course landing page)

- Recommended: finish (or be comfortable with) the Python course. Unit 1 leads with a
  Python→C contrast, so a programming-from-scratch learner should be pointed at Python first.
- No local install, no editor setup, no prior C or assembly. Everything needed for Units
  1–10 and Checkpoints A–E loads in the browser.

---

# Part I — The Course (all in-browser)

## Unit 1 — The C Environment
How C differs from Python: compiled vs. interpreted, static typing, manual memory. The
compilation pipeline at a high level (source → preprocess → compile → link → run) framed as
"what the Run button does for you." Writing and running a first program. `#include`,
`main()`, `return 0`. The preprocessor in brief.

## Unit 2 — Types, Variables, and Operators
Primitive types (`int`, `float`, `double`, `char`). Declaring vs. initializing — and the
hazard of reading an **uninitialized** variable (first taste of undefined behavior). Integer
vs. floating-point arithmetic. Type casting. `sizeof` and why sizes matter. `printf` /
`scanf` with format specifiers (`%d`, `%f`, `%c`, `%s`). Bitwise operators (`&`, `|`, `^`,
`~`, `<<`, `>>`). Operator precedence.

## Unit 3 — Control Flow
`if` / `else if` / `else`, `switch`. `while`, `do-while`, `for`. `break` and `continue`.
Comparison and logical operators. Common beginner traps (`=` vs `==`, fallthrough in
`switch`).

## Unit 4 — Functions
Declaring vs. defining functions, return types, parameters. The call-stack mental model.
Recursion. `void` functions. Header files and `#include` basics (`stdio.h`, `math.h`).
**`argc` / `argv`** (so command-line input is taught before the projects that use it).

### ★ Checkpoint A — Command-Line Calculator (browser)
`argc`/`argv` simulated through the IDE's arg input, string-to-number parsing, type
conversion, branching on the operator. Reinforces Units 2–4. Hidden tests check each
operation and malformed input.

## Unit 5 — Arrays and Strings
Fixed-size arrays. Indexing and iteration. C strings as `char[]`, the null terminator and
why it matters. `string.h` (`strlen`, `strcpy`, `strcmp`, `strncpy`). Multi-dimensional
arrays. **Buffer overruns** introduced concretely (writing past the end / forgetting the
`\0`) — sanitizer-backed exercises make this fail loudly.

### ★ Checkpoint B — Tic-Tac-Toe (CLI, browser)
2D array board, control-flow game loop, win/draw detection, input validation. Reinforces
Units 3–5. Hidden tests drive scripted move sequences and assert board/winner state.

## Unit 6 — Pointers
Address vs. value. `*` and `&`. Pointer arithmetic. Pass-by-pointer vs. pass-by-value.
`NULL`. Pointers and arrays (array decay). Dangling pointers. "The thing Python hides from
you." Heavy use of small, sanitizer-checked exercises.

## Unit 7 — Dynamic Memory
`malloc`, `calloc`, `realloc`, `free`. Heap vs. stack. Memory leaks — what they are, how to
spot them, and (in-browser) how the ASan/leak report flags them. Double-free and
use-after-free as named hazards.

### ★ Checkpoint C — Linked List from Scratch (browser)
The classic rite of passage: `struct` node, dynamic allocation, insert/delete/traverse,
free the whole list. Reinforces Units 6–7. Hidden tests check structural correctness **and**
the leak/UB sanitizer pass must be clean.

## Unit 8 — Structs
Defining structs, fields, initialization. Arrays of structs. Pointers to structs (`->`).
`typedef`. Brief intro to `enum` and `union`. `.` vs `->`.

### ★ Checkpoint D — Student Grade Book (browser)
Structs + arrays of structs + simulated CSV parsing + simple file I/O (see Unit 9 note).
Reinforces Units 5–8. Hidden tests check parsing, averages, and lookups.
> Sequencing note: if you want File I/O available here, either move Unit 9 before this
> checkpoint or keep the grade-book's persistence to in-memory/simulated files. Recommended:
> swap Units 8 and 9 order, or place Checkpoint D after Unit 9.

## Unit 9 — File I/O
`fopen` / `fclose`, `fread` / `fwrite`, `fprintf` / `fscanf`, `fgets`. Text vs. binary mode.
Error handling with `errno` and `perror`.
> Browser note: back files with an in-memory virtual filesystem (the WASM runtime provides
> one; Pyodide already does the equivalent). Learners use the real C file API; it just reads
> and writes a sandboxed FS seeded by the exercise.

## Unit 10 — Standard Library, Scope, the Preprocessor & Multi-file Builds
`stdlib.h`, `time.h`, `limits.h` — what's useful and why. Variable scope and lifetime.
`static` variables. **Preprocessor & macros** (`#define`, function-like macros, header
guards, conditional compilation) — promoted to first-class here. Compilation units and basic
linking: declaration vs. definition across files, multiple `.c` files, `gcc file1.c file2.c
-o program` (shown as the concept the Run button performs).

### ★ Checkpoint E — Word Frequency Counter (browser)
Strings + dynamic memory + a hash-map-ish or sorted-array tally + sorting + file I/O. A
satisfying integrative capstone for the in-browser course. Reinforces Units 5–10. Hidden
tests check counts, ordering, and a clean sanitizer pass.

---

## A short stop before the Advanced Tracks: Debugging & Memory Tools (browser, optional unit)
Reading compiler errors/warnings systematically; interpreting an AddressSanitizer/UBSan
report; the *concept* of Valgrind and `gdb` (full hands-on `gdb` belongs in the local
Advanced Tracks). Function pointers and `const` correctness can also live here as a short
"odds and ends C beginners still need" section.

---

# Part II — Advanced Tracks (LOCAL environment, optional, post-course)

These are explicitly framed as **"graduate to a real environment"** projects. They assume the
learner finished Part I. The first thing each track does is a guided **environment setup**,
because experiencing the setup is part of the point.

## Track Onboarding — Your Local Environment
- Install a compiler toolchain (GCC/Clang) for the learner's OS.
- Choose an editor. **Default recommendation: VS Code** (lowest friction). **Vim is offered
  as an optional path** with a 15-command starter guide (`i`, `Esc`, `:w`, `:q`, `:wq`,
  `:q!`, `dd`, `yy`/`p`, `u`, `/term`, `n`/`N`, `gg`/`G`, `:set number`) — recommended only
  for learners who want it, never required.
- Compile-run cycle from the terminal: `gcc file.c -o program && ./program`, plus
  `-Wall -Wextra -g` and a sanitizer build.
- First hands-on `gdb` session here (now that there's a real terminal).

## Advanced Track 1 — Write a C Compiler (local)
Nora Sandler's series, **targeting x86-64** (not 32-bit — modern Apple Silicon / ARM and
recent macOS make 32-bit x86 impractical to assemble and run; use the x86-64 path). The
compiler grows in stages and is built in C:

- **Stage 1:** lexer + recursive-descent parser + codegen for `return <integer>;` → emit
  `.s`, assemble with GCC, check exit code.
- **Stage 2:** unary operators `-`, `~`, `!`.
- **Stage 3:** binary arithmetic `+ - * /` with precedence.
- **Stage 4:** relational/logical operators (`&& || == != < <= > >=`) via FLAGS + `set*`.
- **Stage 5:** local variables, stack frames (prologue/epilogue), declare/assign/reference.
- **Stage 6:** `if` statements and the ternary `?:` (conditional jumps + labels).
- **Stage 7:** loops (`while`, `do-while`, `for`).
- **Stage 8:** `break`/`continue` + block scoping.
- **Stage 9:** functions + the calling convention; compiles "Hello, World!" via `putchar`.
- **Stage 10:** global variables (`.data`/`.bss`, label references, shadowing rules).

> Note: this track teaches the assembly it emits as it goes — that assembly is **not** a
> prerequisite from Part I, so each stage must introduce the instructions it needs.

## Advanced Track 2 — Build a Small OS (local)
Cross-compiler (i686-elf or x86_64-elf GCC + Binutils) + QEMU. Document the ARM-Mac setup
pain up front.

- **Milestone 1:** cross-toolchain + QEMU; minimal bootloader prints "Hello" via BIOS,
  loaded by GRUB, hands off to a C kernel entry. Prove the toolchain end-to-end.
- **Milestone 2:** C kernel entry + VGA text driver (`0xB8000`), `kprint()`, `kmain()` banner.
- **Milestone 3:** physical memory manager (bitmap) + x86 paging + page-fault handling.
- **Milestone 4:** IDT + PIC remap + PS/2 keyboard IRQ; scan-code translation and echo.
- **Milestone 5:** simple shell (`help`, `clear`, `echo`) + a `task_t`/round-robin
  multitasking skeleton driven by the timer IRQ.

---

# Capstone (local or browser, learner's choice)
**Toy Memory Allocator** — implement `malloc`/`free` over a fixed buffer. Works in-browser
(it's pure C) but pairs naturally with the advanced tracks. The ultimate "you now understand
the layer beneath you" project.

---

# C Cheat Sheet (separate page, parallel to the Python cheat sheet)

1. **Compilation** — the compile-run cycle, `-Wall -Wextra -g -std=c11`, sanitizer build
   `-fsanitize=address,undefined`, `-O` levels.
2. **Types & Variables** — primitives, `sizeof`, type limits from `limits.h`, casting.
3. **Operators** — arithmetic, comparison, logical, **bitwise**, precedence table.
4. **Control Flow** — `if/else`, `switch`, `for`, `while`, `do-while`, `break`/`continue`.
5. **Functions** — declaration vs. definition, pass by value vs. pointer, `void`, `argc`/`argv`.
6. **Pointers** — declaration, dereferencing, pointer arithmetic, `NULL`, array decay.
7. **Strings** — `char[]`, null terminator, key `string.h` functions.
8. **Memory** — `malloc`/`calloc`/`realloc`/`free`, stack vs. heap, leaks/UAF/double-free.
9. **Structs** — definition, initialization, `->` vs. `.`, `typedef`, `enum`/`union`.
10. **Preprocessor** — `#include`, `#define`, function-like macros, header guards.
11. **File I/O** — `fopen` modes, `fprintf`/`fscanf`/`fgets`, `fclose`, `errno`/`perror`.
12. **Local toolchain quick reference** (for the Advanced Tracks only) — GCC flags, `gdb`
    basics, and an **optional** Vim 15-command block.

---

## Summary of changes from v1

- **Browser-first.** All 10 units + Checkpoints A–E run in the existing in-browser IDE with
  hidden-test grading; sanitizer-backed tests give C the automated feedback loop.
- **Compiler & OS moved to optional, post-course, local Advanced Tracks** — reframed as a
  deliberate "graduate to a real environment" experience, with their own guided setup.
- **Checkpoints re-scoped** to the well-calibrated beginner projects (calculator, tic-tac-toe,
  linked list, grade book, word-frequency counter), each reinforcing the unit before it.
- **Vim de-mandated** — default editor is the in-browser IDE; Vim is an optional path inside
  the Advanced Tracks, never a prerequisite to learn C.
- **Content gaps filled** — `argc`/`argv`, `sizeof`, bitwise operators, preprocessor/macros,
  `enum`/`union`, function pointers/`const`, and explicit undefined-behavior/memory-safety
  treatment throughout.
- **Compiler retargeted to x86-64** to avoid the 32-bit-on-modern-hardware wall.
- **Open sequencing question:** order of Units 8 (Structs) and 9 (File I/O) relative to the
  Grade Book checkpoint — recommend File I/O before the grade book, or keep its persistence
  in-memory.
