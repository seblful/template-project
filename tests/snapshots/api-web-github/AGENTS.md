# AI Coding Guidelines

## Core Principles

**Flag bad ideas. Don't silently comply.** If a request conflicts with a project convention, is an antipattern for this stack, or risks security, correctness or maintainability, name the tension in one sentence — then proceed or ask, don't lecture. If the user confirms anyway, comply and move on.

**Every task needs a check that can fail.** Restate the request as something verifiable — a test, a command, an observable output — then work until it holds. If a task admits no such check, say so before starting instead of calling it done by inspection.

______________________________________________________________________

## Project Standards

- **Tests**: Every feature and bug fix requires tests
- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/), subject ≤ 50 chars, imperative mood; no body unless the change needs a "why" (then max 5 bullets); no "Co-Authored-By" footers
- **Docstrings and comments**: Google style, one imperative summary line ending in a period (`Return the cached settings.`), `Args:` on public functions only. Comments are short and explain *why* a design choice was made; never restate what the code already says
- **Logging**: `from demo_proj.logging import get_logger` — structured key-value pairs (`log.info("user saved", user_id=uid)`), never f-strings, never secrets or PII
- **Config**: New settings go in `src/demo_proj/settings.py` *and* in `.env.example`; a test asserts the two stay in sync
- **Features**: each one is a package under `src/demo_proj/`, shaped like `health/`: `router.py` for HTTP only, `schemas.py` for the request and response models, `service.py` for the logic, with no FastAPI imports so it is testable without HTTP. Every route lives under `/api`
- **Web app**: lives in `web/`, a self-contained Bun project. Pages in `web/src/routes/` only arrange features; each feature is a folder in `web/src/features/`, shaped like `health/`, with every component's `*.test.tsx` beside it. A new route is a new file in `routes/`; `src/routeTree.gen.ts` is generated from them, never edited by hand
- **Web code**: strict TypeScript; no `any` and no non-null `!`. A one-sentence `/** ... */` on each exported component and function. Data from outside the app is parsed at the boundary, never cast
- **Web dependencies**: `bun add` inside `web/`, never npm, pnpm or yarn; `web/bun.lock` is committed
- **API contract**: `web/src/api/` holds `openapi.json` and `client.ts`, both generated from the API by `bun run --cwd web generate`, which a hook runs whenever `src/` changes; never edit them by hand. The app calls the API only through the functions in `client.ts`, one per route and named after it, so a changed response model fails the type check wherever the app reads it
- **Imports**: `demo_proj/__init__.py` exports only metadata, on purpose — import from the module that owns the name, not the package root

### Checks

A task is verified against every check the project has: lint, format, types, secret scan, tests with coverage, the production build and the docs build. Fix what they report; never skip the hooks with `--no-verify`.

```bash
uv run prek run --all-files --hook-stage manual
```

`.pre-commit-config.yaml` is where the checks are defined. Add a new one there, not to CI.

### Stack

| Tool | Purpose |
|:-----|:--------|
| [uv](https://docs.astral.sh/uv/) | Package manager — never use `pip` or `venv` |
| [Ruff](https://docs.astral.sh/ruff/) | Linting and formatting |
| [ty](https://github.com/astral-sh/ty) | Type checking |
| [pytest](https://pytest.org/) | Testing + coverage |
| [prek](https://prek.j178.dev/) | Git hooks, reading `.pre-commit-config.yaml` |
| [mdformat](https://mdformat.readthedocs.io/) | Markdown formatting |
| [Zensical](https://zensical.org/) | Documentation (`uv sync --group docs`) |
| [FastAPI](https://fastapi.tiangolo.com/) | HTTP API, served by [uvicorn](https://www.uvicorn.org/) |
| [structlog](https://www.structlog.org/) | Structured logging |
| [pydantic](https://docs.pydantic.dev/) | Data validation and settings |
| [typer](https://typer.tiangolo.com/) | CLI entry points |
| [Bun](https://bun.sh/) | Package manager and script runner for `web/` |
| [Biome](https://biomejs.dev/) | Linting and formatting for `web/` |
| [TypeScript](https://www.typescriptlang.org/) | Type checking (`tsc`, strict) |
| [Vitest](https://vitest.dev/) | Testing, with [Testing Library](https://testing-library.com/) |
| [Vite](https://vite.dev/) | Dev server and production build |
| [React](https://react.dev/) | UI, routed by [TanStack Router](https://tanstack.com/router), data via [TanStack Query](https://tanstack.com/query) |
| [Tailwind CSS](https://tailwindcss.com/) | Styling |

______________________________________________________________________

## Security

- **Never** hardcode secrets — they live in the environment or a gitignored `.env`, wrapped in `SecretStr`, and `.env` is never committed
- Never auto-run destructive commands (`rm -rf`, `del /s`, `curl | sh`)
- Respect `.ignore` paths (every `.env` file except `.env.example`, `secrets/`, `.ssh/`)
