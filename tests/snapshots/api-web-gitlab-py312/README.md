# demo-proj

A generated demo project.

## Setup

Needs [uv](https://docs.astral.sh/uv/), which brings its own Python 3.12, and [Bun](https://bun.sh/) for the web app.

```bash
uv sync
bun install --cwd web
```

## Usage

```bash
uv run demo-proj serve            # interactive docs at http://127.0.0.1:8000/api/docs
uv run demo-proj serve --reload   # restarts on source changes, for development
uv run demo-proj openapi          # the OpenAPI schema, as JSON
```

Each feature is a package under `src/demo_proj/`, shaped like `health/`: `router.py` holds the HTTP routes and nothing else, `schemas.py` the request and response models, and `service.py` the logic, free of FastAPI so it is testable without HTTP. Every route lives under `/api`, which leaves the other paths free for a web app on the same origin.

The web app lives in `web/`, a self-contained [Bun](https://bun.sh/) project:

```bash
bun run --cwd web dev     # http://localhost:5173, reloads as you edit
bun run --cwd web build   # static files in web/dist
```

It is React, [TanStack Router](https://tanstack.com/router) and [TanStack Query](https://tanstack.com/query), styled with [Tailwind CSS](https://tailwindcss.com/), built by [Vite](https://vite.dev/). `src/routes/` holds the pages, which only arrange features; `src/features/` holds the features, each with its components and their tests side by side, as `health/` shows. A file in `src/routes/` is a route at the matching URL: `index.tsx` is `/`, `__root.tsx` the layout around every page. `src/routeTree.gen.ts` is generated from them and committed, so every link is type-checked against the real routes; never edit it by hand.

`web/src/api/` is the contract between the two: `openapi.json`, exported from the API, and `client.ts`, generated from it by [Orval](https://orval.dev/): a typed `fetch` function per route, named after the route function, such as `readHealth()`. A renamed field in a Pydantic model breaks the type check of every component that reads it. A hook regenerates both files whenever `src/` changes; commit what it writes.

In development, run `serve --reload` and the dev server side by side: the dev server forwards `/api` to the API on port 8000, so both share one origin, as they should behind one host in production.

## Configuration

Settings come from environment variables such as `LOGGING__FORMAT=json`, where `__` separates a group from its field. A dotenv file is read only when you select it:

```bash
cp .env.example .env   # local overrides, gitignored
uv run demo-proj serve --env-file .env
```

In Python, pass the same path to `load_settings(env_file=...)`.

Highest priority first: constructor arguments, environment variables, the `.env` file, defaults. A missing selected path, or a misspelled key inside a group, fails at startup.

To add a setting, add a field to a group in `src/demo_proj/settings.py` (use `SecretStr` for secrets) and list it in `.env.example`. A test checks that they match. To read a TOML file as well, override `settings_customise_sources` on `Settings`, as the [pydantic-settings documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#customise-settings-sources) shows.

## Logging

Logs go to stderr as text, or as JSON with `LOGGING__FORMAT=json`, uvicorn's access and error logs included. `LOGGING__LEVEL` sets the lowest level that is logged.

## Development

```bash
uv run prek run --all-files --hook-stage manual   # every check, as CI runs it
uv run --group docs zensical serve                # docs at http://localhost:8001
```

Commits run lint, formatting and types, and check that the message is a [Conventional Commit](https://www.conventionalcommits.org/); pushes run the tests, the production build and the docs build.

For the weekly dependency audit, add a pipeline schedule in GitLab with `SCHEDULED_AUDIT` set to `1`. The `pages` job publishes the docs when run manually.
