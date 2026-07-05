# Module 02 — Types, Variables, and Operators

> In C, every value has a type you choose, a size you can measure, and rules you need to know before the math behaves the way you expect.

In Module 1 you printed a message. Now you'll store and work with data. The big shift from Python is that you pick the *type* of every variable yourself, and that choice changes how much memory it uses and how arithmetic behaves. Get comfortable with types here and the rest of C gets a lot easier.

## Prerequisites

- Module 1 (you can write, read, and Run a basic C program)

## What you'll learn

- The core primitive types: `int`, `float`, `double`, and `char`
- The difference between declaring and initializing — and why reading an uninitialized variable is dangerous
- How integer and floating-point arithmetic differ, and how to cast between types
- How `printf` and `scanf` use format specifiers (`%d`, `%f`, `%c`, `%s`)
- What `sizeof` tells you and why sizes matter
- The bitwise operators and how operator precedence decides what runs first

---

## The primitive types

A variable is a labeled box that holds a value. In C, you also have to say what *kind* of value goes in the box, and you say it once, up front. Here are the four you'll use most:

- `int` — a whole number, like `42` or `-7`
- `float` — a number with a decimal point, single precision, like `3.14`
- `double` — also a decimal number, but double precision (more digits, more accuracy)
- `char` — a single character, like `'A'` (note the single quotes)

```c
#include <stdio.h>

int main(void) {
    int age = 30;
    float price = 9.99f;
    double pi = 3.14159265358979;
    char grade = 'A';

    printf("age: %d\n", age);
    printf("price: %f\n", price);
    printf("pi: %f\n", pi);
    printf("grade: %c\n", grade);
    return 0;
}
```

Press **Run** and you'll see:

```
age: 30
price: 9.990000
pi: 3.141593
grade: A
```

A few things to notice. The `f` after `9.99` marks it as a `float` literal rather than a `double`. A `char` holds one character in single quotes — `'A'`, not `"A"`. And each type prints with its own format specifier in `printf`, which is the next thing we'll cover.

> **Watch out:** `char` and string are not the same thing. `'A'` (single quotes) is one character. `"A"` (double quotes) is a string — an array of characters. Mixing them up is one of the most common early C errors, and the compiler will warn you about it.

---

## Declaring vs. initializing

There are two separate steps when you make a variable. *Declaring* tells the compiler the name and type. *Initializing* gives it a starting value. You can do both at once, or split them up:

```c
int score;        // declared, but NOT initialized — holds garbage
score = 100;      // now initialized
int lives = 3;    // declared and initialized in one line
```

Here's the part that bites beginners. When you declare a variable without giving it a value, it doesn't start at zero. It holds whatever random bits were already sitting in that memory. Reading it before you set it gives you an unpredictable value — this is your first taste of *undefined behavior*.

```c
#include <stdio.h>

int main(void) {
    int x;            // never initialized
    printf("%d\n", x); // reads garbage
    return 0;
}
```

This might print `0`, or `32766`, or some huge negative number. It might even print something different each time you Run it. The program isn't "broken" in a way the compiler must reject — it's just doing something undefined, which is worse, because it can look fine in testing and fail later.

> **Watch out:** Always initialize before you read. Reading an uninitialized variable is undefined behavior — the value is unpredictable and the program may behave differently every run. When in doubt, initialize to `0`.

---

## Integer vs. floating-point arithmetic

You saw this at the end of Module 1: dividing two `int`s throws away the fractional part. That's not a bug, it's how integer arithmetic works. The result of an operation depends on the *types* of the operands, not on what you wish the answer were.

```c
#include <stdio.h>

int main(void) {
    int a = 7, b = 2;
    printf("%d\n", a / b);      // integer division
    printf("%f\n", 7.0 / 2.0);  // floating-point division
    return 0;
}
```

Run it and you'll see:

```
3
3.500000
```

`7 / 2` is `3` because both sides are `int`, so C does integer division and drops the `.5`. `7.0 / 2.0` is `3.5` because the `.0` makes them `double`s. If even one operand is floating-point, C promotes the other and gives you a floating-point result.

> **Watch out:** `5 / 9 * 100` is `0`, not `55`. C evaluates `5 / 9` first as integer division (which is `0`), then `0 * 100` is still `0`. Reorder to `5 * 100 / 9`, or make a value floating-point, to get a sensible answer.

---

## Type casting

Sometimes you have `int`s but you want a floating-point result. A *cast* tells C to treat a value as a different type for that one operation. You write the target type in parentheses in front of the value:

```c
#include <stdio.h>

int main(void) {
    int total = 7;
    int count = 2;
    double average = (double)total / count;
    printf("%f\n", average);
    return 0;
}
```

Run it and you'll see:

```
3.500000
```

Casting `total` to `double` forces floating-point division, so the `count` gets promoted too and you get `3.5` instead of `3`. Casts work the other way as well: `(int)3.9` chops off the decimal and gives you `3` (it truncates toward zero, it does not round).

> **Watch out:** A cast changes the type, not just the display. `(int)3.9` is `3`, and `(int)-3.9` is `-3` — the fractional part is dropped, never rounded. If you need rounding, that's a separate step (we'll meet `round` from `math.h` later).

---

## printf and scanf with format specifiers

`printf` doesn't guess how to display a value — you tell it with a *format specifier*, a `%` code that stands in for a value you pass after the string. Each type has its own:

- `%d` — `int`
- `%f` — `float` or `double`
- `%c` — `char`
- `%s` — string (`char` array)

```c
#include <stdio.h>

int main(void) {
    int n = 5;
    double r = 2.5;
    char c = 'Z';
    printf("n=%d r=%f c=%c\n", n, r, c);
    return 0;
}
```

Run it and you'll see:

```
n=5 r=2.500000 c=Z
```

`scanf` is the mirror image: it reads typed input into your variables. It uses the same specifiers, but you pass the *address* of each variable with `&` so `scanf` knows where to store what it reads.

```c
#include <stdio.h>

int main(void) {
    int age;
    printf("Enter your age: ");
    scanf("%d", &age);
    printf("Next year you'll be %d\n", age + 1);
    return 0;
}
```

Press **Run**, type a number when prompted, and the program echoes back your age plus one. That `&` is the *address-of* operator — it means "where this variable lives in memory." We'll cover addresses properly in Module 6. For now, just remember: `scanf` needs the `&`.

> **Watch out:** Forgetting the `&` in `scanf` — writing `scanf("%d", age)` instead of `scanf("%d", &age)` — is a classic crash. Without the `&`, `scanf` writes to a bogus location and your program misbehaves. The compiler usually warns you, so read the warnings.

---

## sizeof and why sizes matter

Every type takes up a fixed number of bytes in memory, and `sizeof` tells you exactly how many. This matters in C in a way it never did in Python, because the size sets the range of values a type can hold — and once you start allocating memory yourself (Module 7), you'll use `sizeof` constantly.

```c
#include <stdio.h>

int main(void) {
    printf("int:    %zu bytes\n", sizeof(int));
    printf("char:   %zu bytes\n", sizeof(char));
    printf("double: %zu bytes\n", sizeof(double));
    return 0;
}
```

On a typical system you'll see:

```
int:    4 bytes
char:   1 bytes
double: 8 bytes
```

A `char` is always 1 byte. An `int` is usually 4 bytes, which is why it can hold roughly ±2 billion and no more. Push an `int` past its limit and it *overflows* — it wraps around to a negative number instead of growing. That's why sizes are worth knowing: the box only holds so much.

> **Watch out:** `sizeof` returns a value of type `size_t`, which prints with `%zu`, not `%d`. Using the wrong specifier here is technically undefined behavior, even if it happens to look right on your machine.

---

## Bitwise operators

Sometimes you want to work on the individual *bits* of an integer rather than its numeric value. The bitwise operators do exactly that. Think of an `int` as a row of on/off switches, and these operators flip and combine them:

- `&` — AND (a bit is 1 only if both inputs are 1)
- `|` — OR (a bit is 1 if either input is 1)
- `^` — XOR (a bit is 1 if the inputs differ)
- `~` — NOT (flips every bit)
- `<<` — left shift (move bits left, like multiplying by powers of two)
- `>>` — right shift (move bits right, like dividing by powers of two)

```c
#include <stdio.h>

int main(void) {
    int a = 6;   // 0110 in binary
    int b = 3;   // 0011 in binary
    printf("a & b = %d\n", a & b);   // 0010 = 2
    printf("a | b = %d\n", a | b);   // 0111 = 7
    printf("a ^ b = %d\n", a ^ b);   // 0101 = 5
    printf("a << 1 = %d\n", a << 1); // 1100 = 12
    return 0;
}
```

Run it and you'll see:

```
a & b = 2
a | b = 7
a ^ b = 5
a << 1 = 12
```

Left-shifting `6` by one bit doubles it to `12`, because shifting left is multiplying by two. These operators feel abstract now, but they show up in real code for flags, masks, and squeezing data into tight spaces. You don't need to memorize them today — just know they exist and what each symbol means.

> **Watch out:** Don't confuse the bitwise operators `&` and `|` with the logical operators `&&` and `||` (Module 3). `a & b` works on bits; `a && b` is a true/false test. Typing one when you mean the other compiles fine and gives wrong answers — a nasty bug to track down.

---

## Operator precedence

When an expression mixes operators, C follows precedence rules to decide what runs first — the same idea as "multiplication before addition" in math. `*`, `/`, and `%` bind tighter than `+` and `-`, which bind tighter than the bitwise and comparison operators.

```c
#include <stdio.h>

int main(void) {
    int result = 2 + 3 * 4;
    printf("%d\n", result);
    return 0;
}
```

Run it and you'll see:

```
14
```

C computes `3 * 4` first (`12`), then adds `2`, giving `14` — not `20`. If you actually wanted `2 + 3` first, parentheses force it: `(2 + 3) * 4` is `20`. When in doubt, add parentheses. They cost nothing and make your intent obvious to the next person reading the code, including future you.

> **Watch out:** Precedence surprises bite hardest with bitwise operators, which bind *looser* than `+`. `1 << 2 + 3` is `1 << 5` (which is `32`), not `(1 << 2) + 3`. Parenthesize bitwise expressions to be safe.

---

## Try it: predict the output

```c
#include <stdio.h>

int main(void) {
    int a = 5;
    int b = 2;
    double c = 5;
    printf("%d\n", a / b);
    printf("%f\n", c / b);
    printf("%d\n", a % b);
    return 0;
}
```

<details>
<summary>Predict the output, then click to check</summary>

```
2
2.500000
1
```

`a / b` is `5 / 2` with two `int`s, so integer division gives `2`. `c / b` has a `double` on the left, so `b` is promoted and you get `2.5`. The `%` operator is the *remainder*: `5 % 2` is `1`, because 2 goes into 5 twice with 1 left over. The type of the operands decides the behavior — that's the whole lesson of this module in three lines.

</details>

---

## Recap

In C you choose a type for every variable, and that choice has consequences. `int` does integer arithmetic and drops fractions; `float` and `double` keep the decimals. Declaring a variable isn't the same as initializing it, and reading one before you set it is undefined behavior, so initialize first. Casts let you switch types for an operation, `printf` and `scanf` need the right format specifier for each type, and `sizeof` tells you how big a type is and therefore how much it can hold. The bitwise operators work on individual bits, and operator precedence decides what runs first — when you're unsure, reach for parentheses. Nail these and the math in your programs will start matching your intentions.

---

## Quiz seeds

- Q: What does `7 / 2` evaluate to in C, and why?
  - ✅ `3`, because both operands are `int`, so C does integer division and drops the fractional part
  - ❌ `3.5`, because division always produces a decimal — that's Python; in C the operand types decide the result
  - ❌ `4`, because C rounds the result — integer division truncates, it does not round

- Q: You write `int x;` and then `printf("%d\n", x);` without ever assigning `x`. What happens?
  - ✅ Undefined behavior — `x` holds whatever was in that memory, so the output is unpredictable
  - ❌ It prints `0` — C does not zero-initialize ordinary local variables for you
  - ❌ It's a compile error — the compiler may warn, but it won't necessarily reject it; the danger is that it runs

- Q: Why do you pass `&age` (not `age`) to `scanf("%d", &age)`?
  - ✅ `scanf` needs the variable's address so it knows where to store the value it reads
  - ❌ The `&` converts the input to an integer — the `%d` specifier handles the type; `&` is the address-of operator
  - ❌ It's optional styling — leaving out `&` writes to a bogus location and causes a crash
