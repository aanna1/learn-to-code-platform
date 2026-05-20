import type {
  ErrorExplainer,
  ErrorExplanation,
  RuntimeError,
} from "@/lib/languages/types";

/**
 * Beginner-friendly translations of common Python error types. Keyed by the
 * error class name exactly as Python reports it (the part before the colon in a
 * traceback's last line). This map is intentionally its own module so it's easy
 * to extend and so other languages can ship their own explainer.
 */
const EXPLANATIONS: Record<string, ErrorExplanation> = {
  NameError: {
    title: "Python doesn't recognize a name you used",
    explanation:
      "You used a variable or function name that Python hasn't seen yet. Usually it's a typo, or the name is defined later in the file (Python reads top to bottom), or you forgot the quotes around a piece of text.",
    fix: "Check the spelling, make sure the name is defined before this line, and wrap any text values in quotes (e.g. \"Ada\" instead of Ada).",
  },
  IndentationError: {
    title: "The spacing at the start of a line is off",
    explanation:
      "Python uses indentation (leading spaces) to tell which lines belong together. This line has too much, too little, or inconsistent indentation compared to the lines around it.",
    fix: "Line up the indentation with the block it belongs to. Use 4 spaces per level and don't mix tabs and spaces.",
  },
  TabError: {
    title: "Tabs and spaces are mixed in the indentation",
    explanation:
      "This block uses tabs in some places and spaces in others. Python can't tell how the lines line up when they're mixed.",
    fix: "Pick spaces (4 per level is the convention) and convert any tabs. Most editors can do this automatically.",
  },
  SyntaxError: {
    title: "Python couldn't make sense of the code's structure",
    explanation:
      "Something about the way the code is written breaks Python's grammar — often a missing colon, an unclosed bracket or quote, or an = where == was meant.",
    fix: "Look at the line shown (and the one just before it) for a missing :, ), ], }, or quote. Check that opening and closing symbols are balanced.",
  },
  TypeError: {
    title: "An operation got the wrong type of value",
    explanation:
      "You tried to combine or use values in a way their types don't allow — like adding a number to a string, or calling something that isn't a function.",
    fix: "Check the types involved. You may need to convert one (e.g. str(age) to join with text, or int(answer) to do math on input).",
  },
  ValueError: {
    title: "The value was the right type but not an acceptable value",
    explanation:
      "The type was fine, but the specific value didn't work for the operation. A classic case is int(\"hello\") — it's a string as expected, but it isn't a number.",
    fix: "Make sure the value actually fits what the function expects before passing it in — for example, that a string really contains digits before calling int() on it.",
  },
  IndexError: {
    title: "You asked for a position that doesn't exist",
    explanation:
      "You indexed into a list or string with a position past its end. A list of length 4 has positions 0, 1, 2, 3 — there is no position 4.",
    fix: "Remember indexing starts at 0. Use len(items) to check the size, or items[-1] to safely get the last element.",
  },
  KeyError: {
    title: "That key isn't in the dictionary",
    explanation:
      "You looked up a key that the dictionary doesn't contain. Keys are case- and type-sensitive, so \"Name\" and \"name\" are different.",
    fix: "Check the key's spelling and case. Use `key in my_dict` to test first, or my_dict.get(key) to get a default instead of an error.",
  },
  ZeroDivisionError: {
    title: "You divided by zero",
    explanation:
      "Division (or modulo) by zero has no defined answer, so Python stops rather than guess.",
    fix: "Check the divisor before dividing — e.g. only divide when the denominator isn't 0.",
  },
  AttributeError: {
    title: "That value doesn't have the method or attribute you used",
    explanation:
      "You used something like value.something, but that value's type doesn't have a `something`. Often the value is None, or a different type than you expected, or the method name is misspelled.",
    fix: "Check what type the value really is (print(type(value))) and confirm the method name. A common cause is a method that returned None being used as if it returned a value.",
  },
  ModuleNotFoundError: {
    title: "Python couldn't find a module you imported",
    explanation:
      "An import refers to a module name Python can't locate. It may be misspelled, or it isn't available in this in-browser environment.",
    fix: "Check the spelling of the import. Note that this site runs Python in your browser, so not every external package is available.",
  },
  ImportError: {
    title: "An import didn't work",
    explanation:
      "Python found the module but couldn't import the specific name you asked for, or the module failed to load.",
    fix: "Check that the name you're importing actually exists in that module, and that the spelling matches.",
  },
  RecursionError: {
    title: "A function called itself too many times",
    explanation:
      "A function kept calling itself without ever stopping, so Python hit its recursion limit. Usually the base case (the condition that stops the recursion) is missing or never reached.",
    fix: "Make sure your function has a stopping condition that it actually reaches, and that each call moves closer to it.",
  },
  OverflowError: {
    title: "A number got too large to handle",
    explanation:
      "A calculation produced a number too big for the operation (most often with floats).",
    fix: "Check for a loop or formula that's growing a value without bound.",
  },
  UnboundLocalError: {
    title: "A local variable was used before it was set",
    explanation:
      "Inside a function, you used a variable before assigning it. Assigning to a name anywhere in a function makes Python treat it as local for the whole function.",
    fix: "Assign the variable before you read it, or if you meant a variable from outside the function, restructure so it's passed in or returned.",
  },
};

export const pythonErrorExplainer: ErrorExplainer = {
  explain(error: RuntimeError): ErrorExplanation | null {
    if (!error.type) return null;
    return EXPLANATIONS[error.type] ?? null;
  },
};
