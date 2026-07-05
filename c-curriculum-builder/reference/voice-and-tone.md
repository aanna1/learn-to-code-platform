# Voice & tone — write every module like this

This voice is distilled from the two reference course transcripts the curriculum is modeled
on: a fast, friendly, project-driven course ("C Programming Full Course 2025") and a gentle,
overview-first beginner course ("C Programming Tutorial" / Giraffe Academy). Both are warm,
plain-spoken, and relentlessly beginner-first. Match that.

## The five rules

1. **Talk to one person, as a friendly mentor.** Second person, present tense. "You'll", "we're
   going to", "let's". Never lecture at the reader from a distance.

2. **No boring intros.** The reference course literally says "I don't like boring introductions,
   so we're just going to jump right in." Open each module with the thing itself or a quick
   relatable framing — not "In this module, we will explore the concept of…".

3. **Explain with everyday analogies, then show code.** A pointer is "like a house address
   written on paper." A variable is "a labeled box that holds a value." Lead with the picture,
   then the smallest possible program that proves it.

4. **Tiny steps, lots of small wins.** Prefer many short, runnable examples over one big one.
   The reference course is built from a dozen little practice projects; mirror that rhythm —
   each concept earns a quick "now you try / press Run and watch."

5. **Be honest about difficulty, and defer gracefully.** When something is genuinely advanced,
   say so and point ahead, the way Giraffe Academy does ("we're gonna talk about pointers in a
   later module — for now, here's all you need"). Reassure rather than intimidate.

## Sentence-level texture

- Short sentences. Concrete verbs. Contractions are welcome.
- Light, occasional humor is fine; never sarcasm at the learner's expense.
- Address the screen the learner actually sees: "press **Run** and you'll see…". (Core modules
  are browser-based — there is no terminal to open.)
- When code prints something, **state the output** and why. Beginners can't predict it yet.
- Celebrate the payoff: "That's it — you just made the program remember a value between runs of
  the loop." Small, genuine encouragement, not hype.

## Do / Don't

| Do | Don't |
|---|---|
| "A pointer just holds an address — like a sticky note with a house number on it." | "A pointer is a variable whose value is the memory address of another variable, thereby enabling indirection." |
| "Press Run. See the 5? That came from `x`." | "Compile the file with gcc and execute the resulting binary in your terminal." |
| "Heads up: forget the `;` and the compiler will complain about the *next* line — confusing, but normal." | "Note: syntactic errors may manifest on subsequent lines." |
| "We'll get to malloc soon. For now, fixed-size arrays are all we need." | "Dynamic allocation is out of scope and will not be discussed." |

## Anti-AI-tells (the humanizer enforces these)

- No "In conclusion", "It's worth noting that", "Let's dive in", "robust", "leverage", "delve".
- No rule-of-three padding ("fast, clean, and efficient") unless it's actually true and useful.
- Don't over-hedge. Say the thing.
- Vary sentence length; don't em-dash every other line.

## Calibration snippets (the target sound)

- Opening energy: "Alright — a `struct` lets you bundle a few related values into one thing.
  Think of a player in a game: a name, a score, a number of lives. Instead of three loose
  variables, you keep them together. Here's the smallest version."
- Deferring complexity: "You'll see `&` show up here. That's the *address* of the variable —
  we'll dig into addresses properly in Module 6. For now, just know it means 'where this lives
  in memory.'"
- After an example: "Run it. You should see `score: 10`. If you got `score: 9`, you probably
  put the `++` in the wrong spot — scroll back up and compare."
