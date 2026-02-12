# ADR 0001: Standardize repository layout

## Context

The project previously mixed inventory formats and used nested playbook composition patterns.

## Decision

Adopt a top-level layout with:
- `dependencies/requirements.yaml`
- `inventory/{hosts,network,vault}.yaml`
- `playbooks/*.yaml` with short descriptive names
- `roles/<role>/{default,tasks,vars}/main.yaml`
- split documentation in `docs/`
- ADR tracking in `adr/`

## Consequences

- Easier navigation and onboarding.
- A consistent place for configuration and architectural records.
- Slight migration overhead for existing references.
