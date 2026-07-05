# Language Expansion Roadmap

Two ranked lists of the **same 20 languages**, so you can cross-reference them:

- **List 1** ranks them by *how easy each is to add to your browser-only (WASM/JS) platform* — easiest first.
- **List 2** ranks them by *how valuable each is for a learner entering the tech industry* — most valuable first, based on 2025–2026 industry data.

A language that ranks high on **both** lists is the obvious next build. A language that's valuable but hard (e.g. Swift, Rust) tells you where a bigger engineering investment would pay off.

> Key concept for List 1: a teaching site has to **compile/run the learner's code in the browser**, so the language's *compiler or interpreter* must itself run client-side (compiled to WASM or written in JS). Interpreted languages with a mature browser VM are easiest; compiled languages need their whole toolchain shipped to the browser, which is the hard part.

---

## List 1 — Ease of implementation (easiest → hardest)

| # | Language | Browser toolchain | Difficulty |
|---|----------|-------------------|------------|
| 1 | **JavaScript** | Runs natively in every browser — no runtime to ship | Trivial |
| 2 | **TypeScript** | Transpiles to JS in-browser (`tsc`, esbuild-wasm, or Babel) | Trivial |
| 3 | **SQL** | `sql.js` — SQLite compiled to WASM, ~1 MB, fully self-contained | Very easy |
| 4 | **Python** | Pyodide (CDN) — **already built** | Easy (done) |
| 5 | **Lua** | Fengari (pure-JS Lua VM) or `wasmoon` (WASM); tiny | Easy |
| 6 | **Ruby** | `ruby.wasm` — official, now mature | Easy |
| 7 | **C** | Clang → WASM — **in progress** in this repo | Moderate (proven) |
| 8 | **C++** | Same Clang/WASM toolchain as C, larger std lib | Moderate |
| 9 | **PHP** | `php-wasm` (Emscripten build) | Moderate |
| 10 | **R** | WebR — R compiled to WASM; large (~30 MB cold load) | Moderate |
| 11 | **Perl** | WebPerl (Emscripten); works but heavy/niche | Moderate |
| 12 | **Go** | TinyGo → WASM (full Go runtime is heavy; TinyGo is lighter) | Moderate–hard |
| 13 | **OCaml** | `js_of_ocaml` — very mature compile-to-JS path | Moderate–hard |
| 14 | **Scala** | Scala.js (compiler-in-browser is the hard part; Scastie uses a backend) | Hard |
| 15 | **Dart** | `dart2js` / Dart-to-WASM | Hard |
| 16 | **Kotlin** | Kotlin/JS or Kotlin/Wasm; compiler is heavy in-browser | Hard |
| 17 | **Java** | CheerpJ / TeaVM / DoppioJVM — JVM in the browser, large | Hard |
| 18 | **C#** | Blazor WebAssembly runs .NET in-browser; big runtime + Roslyn | Hard |
| 19 | **Rust** | `rustc` in-browser is experimental/heavy; the Rust Playground uses a server | Very hard |
| 20 | **Swift** | SwiftWasm exists, but the toolchain is huge and hard to host client-side | Hardest |

**Reading it:** items 1–8 are realistic near-term adds (most are a few days of adapter + content work). Items 9–13 are doable with a heavier runtime download. Items 14–20 either need a very large in-browser compiler or realistically push you toward a build server — which reintroduces per-use cost and the "free" tradeoff.

---

## List 2 — Industry relevance (most valuable → least, for entering the industry)

Ranked on a blend of 2025–2026 signals: job demand and salary, breadth of use, current momentum, and beginner ROI. Where a placement is genuinely debatable I've said so.

| # | Language | Primary industry use | Why it ranks here |
|---|----------|----------------------|-------------------|
| 1 | **Python** | AI/ML, data science, backend, automation | #1 on the TIOBE Index (~22% share); top job demand; best beginner ROI |
| 2 | **TypeScript** | Web (front + back end via Node) | Rose to **#1 on GitHub in 2025**; the AI-era default for new web code |
| 3 | **JavaScript** | Web front-end & back-end | The only language native to every browser; ~66% developer usage |
| 4 | **SQL** | Databases / data engineering | Near-universal; almost every backend, data, and analytics job needs it |
| 5 | **Java** | Enterprise backend, Android | Enormous, stable job base; banks, big tech, Android legacy |
| 6 | **C#** | Enterprise (.NET), game dev (Unity) | Strong, durable demand; the Unity engine makes it the indie-games default |
| 7 | **Go** | Cloud infrastructure, DevOps, backend | Fast-growing, high pay; the language of Docker/Kubernetes-era infra |
| 8 | **C++** | Systems, games, embedded, finance (HFT) | Durable high-performance niche; high salaries; foundational |
| 9 | **Rust** | Systems, blockchain, performance-critical | **Most-admired language**; fastest-rising, among highest-paid (adoption still modest) |
| 10 | **Kotlin** | Android (primary), JVM backend | The official modern Android language; solid mobile job market |
| 11 | **Swift** | iOS / macOS apps | The only path to native Apple apps — big market, but single-platform |
| 12 | **C** | Embedded, OS, systems, teaching | Smaller direct job pool but foundational; underpins everything |
| 13 | **PHP** | Web backend (WordPress, legacy) | Declining mindshare but still powers a huge share of the web → many jobs |
| 14 | **Ruby** | Web (Rails), startups | Past its peak, but Rails still has a healthy startup/job ecosystem |
| 15 | **R** | Statistics, data science, academia, pharma | Niche but valuable and well-paid in research/analytics |
| 16 | **Dart** | Cross-platform mobile (Flutter) | Growing with Flutter; moderate but rising job demand |
| 17 | **Scala** | Big data (Spark), fintech | Strong in data-engineering pockets; overall mindshare shrinking |
| 18 | **Lua** | Game scripting, embedded | Roblox, game engines, Redis/Neovim/nginx — alive but specialized |
| 19 | **Perl** | Legacy systems, sysadmin, bioinformatics | Declining; mostly maintenance roles now |
| 20 | **OCaml** | Compilers, fintech (Jane Street), academia | Highly respected but very niche hiring |

**Debatable spots worth knowing:** Rust vs. Kotlin/Swift (Rust = future-proofing and pay; mobile = more raw job volume *today* if you specifically want app dev). Dart could rank above R/Ruby if Flutter keeps growing. These are close calls, not hard facts.

---

## How to read the two lists together

The sweet spot — **easy to build AND highly valuable** — is the top of both lists: **TypeScript, JavaScript, SQL** (and Python, already done). These should be your next additions; they're nearly free to implement and they're exactly what employers want most.

The strategic tension is at the bottom of List 1: **Rust, Swift, C#, Java, Kotlin** are all industry-valuable but hard to run client-side. For a free, browser-only platform, the most cost-effective coverage is roughly the **top ~13 of List 1**, which still includes most of the highest-value languages (Python, TS, JS, SQL, C/C++, Go, Ruby, R). The handful that are both hard *and* high-value are exactly the ones that would tempt you toward a paid build-server — the same economics that make competitors paywall them.

---

## Sources

- [2025 Stack Overflow Developer Survey — Technology](https://survey.stackoverflow.co/2025/technology)
- [TIOBE Index, June 2026 (TechRepublic)](https://www.techrepublic.com/article/news-tiobe-index-language-rankings/)
- [GitHub Octoverse 2025 — TypeScript reaches #1 (GitHub Blog)](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/)
- [TypeScript Tops GitHub Octoverse (Visual Studio Magazine)](https://visualstudiomagazine.com/articles/2025/10/31/typescript-tops-github-octoverse-as-ai-era-reshapes-language-choices.aspx)
- [Most In-Demand Programming Languages 2025 (Monash Online)](https://online.monash.edu/news/most-in-demand-programming-languages-2025/)
- [Best Programming Languages to Learn in 2026 (Analytics Insight)](https://www.analyticsinsight.net/education/best-programming-languages-to-learn-in-2026)
