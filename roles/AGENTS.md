# Roles Agent Guide

Scope: `roles/` subtree.

- Keep role layout as `defaults/`, `tasks/`, `vars/`.
- Entry points must remain `main.yaml` in each subdirectory.
- Keep role-related Ansible files in `.yaml` format; `ansible.cfg` is outside role scope and is the known config exception.
- Prefer hierarchical config keys from `inventory/network.yaml`.
- Prefer `ansible.builtin.raw` for device-side command execution since Python may not be available on managed network targets.
- If role behavior changes significantly, add/update an ADR in `adr/`.
