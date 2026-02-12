# Agent Operating Guide

Scope: entire repository.

## Required behavior for contributors and AI agents

- Preserve the standard layout defined in `docs/structure.md`.
- Keep inventory in `inventory/*.yaml` only.
- Keep playbooks in `playbooks/*.yaml` using short names.
- Keep each role in `roles/<role>/{defaults,tasks,vars}/` with `main.yaml` files.
- For Ansible artifacts (playbooks, roles, tasks, defaults, vars, inventory), use `.yaml` consistently where possible; `ansible.cfg` is the only intentional non-YAML config file.
- Prefer `ansible.builtin.raw` for commands on managed routers/devices because Python may not be installed; use Python-dependent modules on targets only when interpreter availability is guaranteed.
- When making architectural or structural changes, add/update an ADR in `adr/`.
- When changing workflows, update docs in `docs/how-to/`.
- Do not re-introduce wrapper playbooks or mixed inventory formats.
