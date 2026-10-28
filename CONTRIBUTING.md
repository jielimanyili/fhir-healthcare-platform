# Contributing

## How we document changes
- **Commits:** Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `chore:`).
- **PRs:** use the PR template — link the ticket, state what / why / how / testing.
- **CHANGELOG:** updated at release time (Keep a Changelog), user-visible changes only.
- **ADRs:** only for significant architectural decisions (`docs/adr/`).

## Development workflow
1. Pick up a story from the tracker.
2. Branch: `feature/<slug>` / `fix/<slug>`.
3. Write code + tests (AI rules + gates: see `docs/ai-assisted-development.md`).
4. Open a PR using the template.
5. Merge after review; CI (lint + test) must pass.

## AI-assisted development
See `docs/ai-assisted-development.md` and `AGENTS.md`.
