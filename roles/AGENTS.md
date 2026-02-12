# Roles Agent Guide

Scope: `roles/` subtree.

- Keep role layout as `default/`, `tasks/`, `vars/`.
- Entry points must remain `main.yaml` in each subdirectory.
- Prefer hierarchical config keys from `inventory/network.yaml`.
- If role behavior changes significantly, add/update an ADR in `adr/`.
