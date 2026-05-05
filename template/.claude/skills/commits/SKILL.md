---
name: commits
description: Git commit conventions, conventional commit format, pre-commit workflow, and commit message best practices.
origin: ECC
---

# Commit Conventions

## Rule

**Only create commits when the user explicitly asks. Never commit proactively.**

## Workflow

```bash
uv run pre-commit run --all-files   # Run checks before committing
git add <files>                      # Stage specific files only
git commit -m "<type>: <description>"
```

Always run pre-commit before committing. Never use `--no-verify` to skip hooks.

## Conventional Commits Format

```
<type>: <description>
```

- Lowercase
- Concise — no trailing period
- Present tense ("add feature", not "added feature")

### Types

| Type | Purpose |
|:-----|:--------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code change with no feature or bug change |
| `test` | Test additions or updates |
| `docs` | Documentation only |
| `chore` | Routine tasks, dependency updates, config |

### Examples

```
feat: add user authentication endpoint
fix: handle None return from database query
refactor: extract validation logic into separate module
test: add parametrized tests for email validator
docs: update README with installation steps
chore: bump ruff to 0.9.0
```

## Scoping (Optional)

Add a scope in parentheses for large codebases:

```
feat(auth): add OAuth2 login flow
fix(cli): handle missing config file gracefully
```

## Breaking Changes

Append `!` for breaking changes:

```
feat!: remove deprecated v1 API endpoints
```

Or add a footer:

```
feat: migrate to new settings format

BREAKING CHANGE: APP_NAME env var renamed to APP__NAME
```

## Staging

Prefer staging specific files over `git add .`:

```bash
git add src/mypackage/auth.py tests/test_auth.py
```

Never stage `.env`, secrets, or generated files.

## AI-Generated Code

Mark AI-assisted commits with:

```
Co-authored-by: Claude Code <noreply@anthropic.com>
```
