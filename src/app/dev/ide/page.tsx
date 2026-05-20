import { Ide, type IdeExercise } from "@/components/ide/Ide";

/**
 * Temporary development harness for the IDE (Phase 2). It mounts the full IDE
 * with a hardcoded exercise so the end-to-end flow can be validated in isolation:
 * editing, real-time linting, Run (with interactive input()), Submit (hidden
 * tests), friendly errors, hints, solution, reset, and keyboard shortcuts.
 *
 * This route is removed/replaced once lessons render the IDE (Phase 3+).
 */
const DEV_EXERCISE: IdeExercise = {
  starter: `def greet(name):
    # Return a greeting like "Hello, Ada!"
    return ""


# Run this to greet yourself interactively:
if __name__ == "__main__":
    user_name = input("What's your name? ")
    print(greet(user_name))
`,
  solution: `def greet(name):
    return f"Hello, {name}!"


if __name__ == "__main__":
    user_name = input("What's your name? ")
    print(greet(user_name))
`,
  tests: `def test_greets_a_name():
    "greet('Ada') returns 'Hello, Ada!'"
    assert greet("Ada") == "Hello, Ada!"

def test_greets_another_name():
    "greet('Sam') returns 'Hello, Sam!'"
    assert greet("Sam") == "Hello, Sam!"

def test_includes_exclamation():
    "the greeting ends with '!'"
    assert greet("Lin").endswith("!")
`,
  hints: [
    "An f-string lets you drop a variable into text: f\"Hello, {name}!\".",
    "Replace the empty return with the f-string, keeping the comma and exclamation mark.",
    "The whole body is one line: return f\"Hello, {name}!\"",
  ],
};

export default function DevIdePage() {
  return (
    <main className="flex h-screen flex-col gap-3 p-4">
      <header className="shrink-0">
        <h1 className="text-lg font-semibold">IDE dev harness</h1>
        <p className="text-sm text-muted">
          Phase 2 validation. Press Run to greet yourself (interactive input), or Submit to run the
          hidden checks.
        </p>
      </header>
      <div className="min-h-0 flex-1">
        <Ide languageId="python" exercise={DEV_EXERCISE} />
      </div>
    </main>
  );
}
