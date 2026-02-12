# Docs Agent Guide

Scope: `docs/` subtree.

- Keep docs concise and task-oriented.
- Update `docs/structure.md` for any directory/layout changes.
- Add or update a `docs/how-to/*` file when workflows change.
- When documenting file creation standards, state that Ansible artifacts should use `.yaml` (except `ansible.cfg`).
- When documenting execution patterns for managed network devices, prioritize `ansible.builtin.raw` because Python may be unavailable.
- If architecture changes, ensure a matching ADR exists under `adr/`.
