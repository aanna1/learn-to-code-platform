# Learn to Code

A free, fully static website for teaching programming to complete beginners — in-depth
lectures plus interactive, browser-based coding exercises. Python first, with an
architecture built so new languages are an adapter + content drop-in, not a refactor.

Everything runs in the browser: no backend, no database, no accounts, no paid services.

## Status

Under active development. **Phase 1 (scaffold + language abstraction) is complete.** See
[`CLAUDE.md`](./CLAUDE.md) for the full build plan and current state, and
[`docs/Claude Code Prompt.md`](./docs/Claude%20Code%20Prompt.md) for the spec.

## Requirements

- Node.js 18+ (developed on Node 24)
- npm

## Local development

```bash
npm install
npm run dev      # http://localhost:3000
```

Other scripts:

```bash
npm run build      # static export to ./out
npm run typecheck  # tsc --noEmit
npm run lint       # Next ESLint
```

## Deployment

The site is a static export (`output: "export"` → `./out`) and can be served from any
static host. The interactive runtime needs cross-origin isolation, so the host must send:

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

On **Vercel** these are configured in [`vercel.json`](./vercel.json). Full deployment
instructions for Vercel and other static hosts (e.g. GitHub Pages) will be added in
Phase 6.
