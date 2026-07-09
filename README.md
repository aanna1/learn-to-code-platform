# Disclaimer

This entire project is vibe-coded just as a fun experiment and also potentially a resource should I ever want to code any of the languages I include within this website. At some point I'd also like to add a file with all my prompts as well as the specific ai and model I used just so that people can see how the website ended up the way it did.

# Learn to Code

A free, fully static website for teaching programming to complete beginners: in-depth
lectures paired with interactive, browser-based coding exercises. Everything runs in the
browser — no backend, no database, no accounts, no paid services.

The codebase teaches **Python**, but "the language being taught" is a parameter: adding
JavaScript, Rust, etc. is an adapter plus a content drop-in, never a refactor.

See [`CLAUDE.md`](./CLAUDE.md) for the full build history and current state, and
[`docs/Claude Code Prompt.md`](./docs/Claude%20Code%20Prompt.md) for the original spec.

## Features

- **Lessons in two layouts** — lectures (MDX prose + inline runnable code + an
  end-of-lecture quiz) and exercises (problem statement + full in-browser IDE).
- **Real Python in the browser** via [Pyodide](https://pyodide.org/) — Run streams
  stdout/stderr to an xterm.js terminal and supports interactive `input()`.
- **Hidden test grading** — Submit runs `tests.py` against the learner's code and reports
  pass/fail per case.
- **Real-time linting** with Ruff (WASM), **friendly error explanations**, progressive
  hints, a reveal-able solution, and per-exercise autosave.
- **Progress tracking** (completion, quiz scores, last-visited) in `localStorage`.
- **Cheat sheet** per language, **light/dark theme**, and a mobile reading mode.

## Tech stack

- [Next.js 14](https://nextjs.org/) (App Router) + TypeScript (strict), `output: "export"`
  (fully static).
- [Tailwind CSS](https://tailwindcss.com/) with CSS-custom-property theming.
- [Monaco editor](https://microsoft.github.io/monaco-editor/) and Pyodide loaded lazily
  from the jsDelivr CDN; [Ruff WASM](https://github.com/astral-sh/ruff) for linting.
- MDX compiled at build time with [`@mdx-js/mdx`](https://mdxjs.com/).

## Getting started

Requires Node.js 18.18+ (the Next.js 14 baseline; developed on Node 24).

```bash
npm install
npm run dev        # http://localhost:3000
```

| Command             | What it does            |
| ------------------- | ----------------------- |
| `npm run dev`       | Local dev server        |
| `npm run build`     | Static export to `out/` |
| `npm run typecheck` | `tsc --noEmit`          |
| `npm run lint`      | Next.js ESLint          |

## Project structure

```
src/
  app/                 # routes (App Router)
    page.tsx                                       # homepage
    learn/[language]/page.tsx                      # course outline
    learn/[language]/[module]/[lesson]/page.tsx    # lesson (lecture or exercise)
    cheatsheet/[language]/page.tsx                 # cheat sheet
  components/
    ide/               # Monaco editor, xterm terminal, resizable split
    lesson/            # MDX renderer, inline Runnable, quiz, outline
    nav/               # site header, theme toggle, mobile nav
    ui/                # buttons, modal, spinner
  lib/
    languages/         # the Language interface + registry + python adapter
    content/           # content loader + MDX compile helper
    progress/          # localStorage progress + autosave
    theme/             # theme tokens + provider
  content/
    languages/python/  # course.json, cheatsheet.mdx, modules/…
```

## Authoring content

Adding a module or lesson is just files — no code changes. Per language, under
`src/content/languages/<lang>/`:

```
course.json                       # language metadata + ordered module list
cheatsheet.mdx                    # the cheat sheet
modules/<moduleId>/
  module.json                     # module metadata + ordered lesson list
  <lessonId>/lecture.mdx          # lecture lesson…
  <lessonId>/quiz.json            #   …with an optional end-of-lecture quiz
  <lessonId>/exercise/            # …or an exercise lesson:
    prompt.mdx                    #   problem statement (MDX)
    starter.py  solution.py       #   starting code + reference solution
    tests.py                      #   hidden graded tests
    hints.json                    #   progressive hints
```

List each new module in `course.json` and each new lesson in its `module.json` (with a
`type` of `"lecture"` or `"exercise"` and an `order`). The loader sorts by `order`.

**MDX authoring notes**

- Prose is plain Markdown. Avoid raw `{`, `}`, `<`, `>` in prose (MDX reads them as
  JSX/expressions) — code fences and inline code are exempt.
- Inline runnable code: `` <Runnable code={`print("hi")`} /> `` (multi-line template
  literals are fine). It inherits the lesson's language automatically.
- Asides: `<Callout type="note | tip | warning">…</Callout>`.

**Test convention (`tests.py`)**

Define `test_*()` functions that call the learner's code and `assert`. The first line of
each function's docstring is shown as the test's friendly name. Put any interactive/demo
code (e.g. `input()`) under `if __name__ == "__main__":` — the grader sets `__name__` to a
non-`"__main__"` value, so that block is skipped during Submit.

## Adding a language

The app never branches on a specific language; all behavior flows through the `Language`
interface (`src/lib/languages/types.ts`). To add one:

1. Implement the interface in `src/lib/languages/<id>/` — `config`, `runtime`, `linter`,
   `errorExplainer`.
2. Register it in `src/lib/languages/registry.ts`.
3. Drop in content under `src/content/languages/<id>/`.

No component or route changes are required.

## Deployment

`npm run build` produces a static site in `out/` that any static host can serve.

### Cross-origin isolation (COOP/COEP)

The interactive terminal uses a `SharedArrayBuffer` so the Pyodide worker can block on
`input()`. Browsers only expose `SharedArrayBuffer` on **cross-origin isolated** pages,
which requires two response headers on every document:

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

Without them, code still runs and output still streams, but `input()` immediately returns
EOF (and Stop falls back to terminating the worker). The browser runtimes — Pyodide and
Monaco (Python), Ruff (linting), and sql.js (the SQLite-WASM engine behind the SQL course)
— are all loaded from the same `cdn.jsdelivr.net` origin, which already sends the
`Cross-Origin-Resource-Policy: cross-origin` header needed to load under `require-corp`, so
no self-hosting is required — but the host must be able to reach the jsDelivr CDN. (The C
course's clang toolchain is the one exception: it exceeds jsDelivr's file-size cap and is
self-hosted same-origin from `public/c-toolchain/`.)

After the first load, `public/coi-serviceworker.js` caches the jsDelivr runtime assets
(Pyodide, Monaco, Ruff, sql.js) in a `runtime-cdn` Cache Storage bucket, so revisits and
subsequent lessons load the engines from disk instead of re-fetching them.

`output: "export"` cannot emit headers itself, so configure them at the host:

- **Vercel** — handled by [`vercel.json`](./vercel.json) in this repo.
- **Local dev** — handled by the `headers()` block in [`next.config.mjs`](./next.config.mjs).
- **Netlify** — add a `_headers` file (or `netlify.toml`) with the two headers for `/*`.
- **Cloudflare Pages / nginx / Apache** — set the two headers on all document responses.
- **GitHub Pages** — cannot set custom headers, so pages are not cross-origin isolated:
  exercises run but interactive `input()` degrades to EOF. If you need isolation there, a
  service-worker shim such as
  [`coi-serviceworker`](https://github.com/gzuidhof/coi-serviceworker) can inject the
  headers client-side.

## License

No license is specified; treat as all rights reserved unless one is added.
