# Agent Operating Guide

Scope: entire repository.

## Required behavior for contributors and AI agents

- Preserve the standard layout defined in `docs/structure.md`.
- Keep inventory in `inventory/*.yaml` only.
- Keep playbooks in `playbooks/*.yaml` using short names.
- Keep each role in `roles/<role>/{default,tasks,vars}/` with `main.yaml` files.
- When making architectural or structural changes, add/update an ADR in `adr/`.
- When changing workflows, update docs in `docs/how-to/`.
- Do not re-introduce wrapper playbooks or mixed inventory formats.
