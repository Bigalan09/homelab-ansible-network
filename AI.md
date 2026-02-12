# AI Collaboration Notes

This file defines how AI tools should operate in this repository.

## Planning expectations

- Prefer incremental, explicit changes.
- Keep naming consistent with existing YAML files.
- Use hierarchical configuration in `inventory/network.yaml`.

## Documentation expectations

- Update `docs/structure.md` when layout changes.
- Update `docs/how-to/` for runbook/process changes.
- Add an ADR entry in `adr/` for non-trivial architectural decisions.

## Validation expectations

- Run available tests.
- Run Ansible syntax checks when `ansible-playbook` is available.
