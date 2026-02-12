# ADR 0002: Require ADR refresh for architecture changes

## Context

The repository already standardizes structure and conventions, but architecture evolves as playbooks, roles, inventory shape, and topology assumptions change. If those changes are not reflected in ADRs, the design record drifts and onboarding/regression review gets harder.

## Decision

For any pull request that changes architecture or structure, update the ADR set in the same change.

Architecture/structure changes include:
- role boundaries, role responsibilities, or role composition in playbooks,
- inventory model/schema changes that affect how hosts/services are represented,
- topology assumptions (gateway/AP responsibilities, VLAN or routing model),
- foundational execution model changes (for example how bootstrap/provisioning is staged).

Implementation requirements:
- create a new ADR when introducing a new decision,
- update an existing ADR when refining or replacing a prior decision,
- mark superseded ADRs clearly by referencing the replacing ADR,
- include links to impacted docs/playbooks/inventory paths.

## Consequences

- Architecture intent stays current with implementation.
- Reviewers get explicit decision context for structural changes.
- Slight additional authoring overhead on architecture-impacting PRs.
