import type {
  ErrorExplainer,
  ErrorExplanation,
  RuntimeError,
} from "@/lib/languages/types";

/**
 * Beginner-friendly translations of the error "types" the C runtime worker emits.
 *
 * Unlike Python, C has no built-in exception class names. The worker is responsible
 * for normalizing both *compile-time* failures and *runtime* faults into a small,
 * stable set of `RuntimeError.type` strings (listed below) so this map stays simple
 * and language-agnostic at the interface. Keep this set in sync with the type strings
 * produced in `c.worker.ts`.
 *
 * Emitted types (the contract):
 *   - "CompileError"        clang/lld rejected the program (syntax, type, undeclared id, link)
 *   - "SegmentationFault"   bad memory access (null/dangling/out-of-bounds pointer)
 *   - "StackOverflow"       runaway recursion / unbounded stack growth
 *   - "FloatingPointError"  integer divide-by-zero or %0
 *   - "AssertionFailed"     an assert() in the program (or a test) failed
 *   - "UndefinedBehavior"   UBSan flagged UB (overflow, OOB, misaligned, etc.)
 *   - "OutOfMemory"         malloc/realloc returned NULL or the heap was exhausted
 *   - "Timeout"             the program ran too long and was stopped
 *   - "NonZeroExit"         main() returned a non-zero status with no other signal
 */
const EXPLANATIONS: Record<string, ErrorExplanation> = {
  CompileError: {
    title: "The compiler couldn't build your program",
    explanation:
      "C is compiled before it runs, so the program never started — the compiler found something it couldn't accept. Common causes are a missing semicolon, an unclosed brace or quote, using a name before it's declared, a type mismatch, or a missing #include.",
    fix: "Read the first error message and its line number (later errors are often just fallout from the first). Check that line and the one above it for a missing ;, }, ), or quote, and make sure every name and function you use is declared or #included.",
  },
  SegmentationFault: {
    title: "Your program touched memory it wasn't allowed to",
    explanation:
      "This is the classic C crash. It usually means a pointer pointed somewhere invalid — it was NULL, it was never set, it pointed at freed memory, or you read/wrote past the end of an array.",
    fix: "Check every pointer is set to a valid address before you use it, that you don't index past the end of an array (a length-4 array has indices 0–3), and that you don't use memory after free().",
  },
  StackOverflow: {
    title: "A function called itself too many times",
    explanation:
      "Each function call uses a bit of stack space. A recursion that never reaches its stopping condition keeps calling itself until the stack runs out.",
    fix: "Make sure your recursive function has a base case it actually reaches, and that each call moves closer to it. If you meant a loop, you may have recursed by accident.",
  },
  FloatingPointError: {
    title: "You divided by zero",
    explanation:
      "Integer division or remainder (% ) by zero has no defined result, so the program is stopped. (Despite the name, this is most often integer division, not floats.)",
    fix: "Check the divisor before dividing — only divide when it isn't 0.",
  },
  AssertionFailed: {
    title: "An assert() check failed",
    explanation:
      "A condition the program promised would be true turned out false at runtime, so assert() stopped the program. In an exercise, this often means a hidden test caught wrong output.",
    fix: "Look at the asserted condition shown in the message — it tells you exactly which assumption broke. Trace back to where that value is computed.",
  },
  UndefinedBehavior: {
    title: "Your program did something C considers undefined",
    explanation:
      "The sanitizer caught behavior the C standard doesn't define — such as signed-integer overflow, reading past an array, shifting by too many bits, or using an uninitialized value. These 'work sometimes' by luck, which makes them dangerous.",
    fix: "Read the sanitizer message and its line number — it names the exact operation. Fix the root cause (bounds-check the index, initialize the variable, widen the type) rather than masking it.",
  },
  OutOfMemory: {
    title: "The program ran out of memory",
    explanation:
      "A call to malloc/calloc/realloc couldn't get the memory it asked for (it returned NULL), or an allocation loop grew without bound.",
    fix: "Check that allocation sizes are reasonable and that a loop isn't allocating forever. Always check whether malloc returned NULL before using the pointer.",
  },
  Timeout: {
    title: "Your program ran too long and was stopped",
    explanation:
      "The program didn't finish in time — usually an infinite loop, or a loop whose exit condition is never met.",
    fix: "Check your loop conditions. Make sure something inside the loop changes the value the condition tests, so it can eventually become false.",
  },
  NonZeroExit: {
    title: "The program exited with an error status",
    explanation:
      "main() (or something it called, like exit()) returned a non-zero value, which by convention signals failure — even though there was no crash.",
    fix: "Check what value you return from main() and any exit() calls. Return 0 for success unless you intend to signal an error.",
  },
};

export const cErrorExplainer: ErrorExplainer = {
  explain(error: RuntimeError): ErrorExplanation | null {
    if (!error.type) return null;
    return EXPLANATIONS[error.type] ?? null;
  },
};
