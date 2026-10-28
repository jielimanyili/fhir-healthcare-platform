# AI-Assisted Development Guide

> How we use AI tools (Copilot / Claude Code / Cursor), and the gates every AI change must pass.

## Scope
**Use AI for:** scaffolding, boilerplate, tests, refactors, docs, rubber-ducking.

**Don't use AI for:** architecture decisions, auth/security, anything you can't review or defend.

## Workflow
draft → review → harden → merge

## Review gates (every AI change)
- ✅ Architecture fit — respects the existing design + ADRs
- ✅ Correctness — edge cases, types, logic
- ✅ Security — no injection, no leaked secrets, no real PHI, least privilege
- ✅ Test coverage — new/changed code has tests
- ✅ Readability — maintainable, idiomatic, no dead code

## Security rules
- Never paste secrets or PII/PHI to AI tools.
- Never commit `.env` or secrets.
- All patient data is synthetic; redact any sensitive data before sharing context.

## Accountability
AI drafts; **the human owns** every line merged.

## Verification
Lint, typecheck, and tests still run in CI regardless of who "wrote" the code.
