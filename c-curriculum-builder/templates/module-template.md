# Module doc template — structure of every `C Curriculum Module NN.md`

Write each output file in this exact order. Prose goes in the course voice
(`reference/voice-and-tone.md`). Keep code blocks short and runnable. This is raw Markdown
(the downstream `curriculum-converter` handles MDX-safety and exercise authoring) — but write
it cleanly so conversion is trivial.

---

```markdown
# Module NN — Title

> One-sentence description (from the master's Description field), in the course voice.

[A 2–4 sentence hook. No "In this module we will…" boilerplate. Open with why this matters or
a quick relatable framing, the way the reference courses jump straight in.]

## Prerequisites

- [from master]

## What you'll learn

- [objective]
- [objective]
- [objective]

## [Concept 1 name]

[Plain-language explanation built from the seed. Work the analogy in naturally. Then a short,
self-contained example the learner can paste and press Run.]

```c
// short, focused example — compiles and runs as-is
#include <stdio.h>

int main(void) {
    // ...
    return 0;
}
```

> **Watch out:** [the concept's gotcha / undefined-behavior note, in one or two sentences.]

## [Concept 2 name]

[…same pattern…]

## Try it: predict the output

```c
// predict-then-reveal code from the master seed
```

<details>
<summary>Predict the output, then click to check</summary>

```
[exact output]
```

[One line on *why* — the teaching payoff.]

</details>

## Recap

[3–6 sentences pulling the module together in plain language. No bullet-point dump unless it
genuinely reads better as a short list.]

## Quiz seeds

[Kept for the converter — 2–3 questions from the master's quiz seeds.]

- Q: [question]
  - ✅ [correct option]
  - ❌ [distractor] — [why it's wrong]
  - ❌ [distractor] — [why it's wrong]

## Checkpoint project   <!-- ONLY if the master marks one for this module -->

**[Project name].** [What the learner builds and why it's satisfying.]

- Skills drilled: [list]
- Done when: [observable definition of done — what the program does / what tests would check]
- Starter shape: [a sentence or two on the scaffold the converter should generate]
```

---

## Notes for the author (do not put these in the output)

- **Browser framing.** For `core` modules, running code = pressing **Run**. Never write "open
  your terminal", "run `gcc file.c`", or "save the file as …" in a core module. Advanced-Track
  modules are the exception and *should* use the real local toolchain.
- **One idea per example.** Mirror the reference courses: many tiny programs beat one big one.
- **Show output.** When an example prints something, say what it prints — beginners can't yet
  predict it.
- **Name the mistake.** Every `Watch out` should name a concrete beginner error or UB, not a
  vague caution.
- **Checkpoint project section appears only when the master's Module list marks one** — most
  modules won't have it.
