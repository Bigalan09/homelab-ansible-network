# Phase 0 Survey and Phase 1 Quality Gates

## Phase 0: repository survey

### Current playbook to role map

- `playbooks/gateway-core.yaml` -> `roles/gateway_router`
- `playbooks/gateway-router.yaml` -> `roles/gateway_router`, `roles/tailscale_openwrt`, `roles/adguard_home_openwrt`, `roles/wireguard_policy_openwrt`
- `playbooks/ap-repeater.yaml` -> `roles/ap_repeater`
- `playbooks/crs310-router-on-stick.yaml` -> `roles/mikrotik_crs310_bridge_vlan`
- `playbooks/tailscale.yaml` and `playbooks/tailscale-nodes.yaml` -> `roles/tailscale_openwrt`
- `playbooks/adguard.yaml` -> `roles/adguard_home_openwrt`
- `playbooks/wireguard-policy.yaml` -> `roles/wireguard_policy_openwrt`

### Duplicated logic and fragile assumptions

1. **Duplicated role entrypoints via service-only and full-stack playbooks**
   - `gateway-router.yaml` includes service roles that are also exposed via single-purpose playbooks.
   - Risk: drift in execution expectations and operator confusion about which run path is authoritative.

2. **`inventory/vault.yaml` is assumed to exist for most OpenWrt playbooks**
   - Syntax and linting fail on a clean clone unless a local vault file is created first.
   - Risk: CI/local checks are skipped or inconsistent.

3. **Host key verification is disabled globally in inventory**
   - `StrictHostKeyChecking=no` and `/dev/null` known_hosts are convenient for rebuilds but weaken SSH trust.
   - Risk: accidental MITM acceptance on management links.

4. **Router/AP automation is heavily command-string based**
   - This is appropriate for no-Python targets, but parsing and idempotency are harder to guarantee.
   - Risk: difficult-to-detect partial apply on unstable links.

5. **Repository structure documentation drifted from the live tree**
   - `docs/structure.md` referenced files/directories not present in the repository and missed active helper scripts.
   - Risk: operator confusion during onboarding and troubleshooting.

### Consistent local development setup

Use this baseline for repeatable local validation:

1. Create a Python virtualenv and install validation tooling:
   - `ansible`
   - `ansible-lint`
   - `yamllint`
   - `pre-commit`
2. Install required collections:
   - `ansible-galaxy collection install -r dependencies/requirements.yaml`
3. Create a non-secret local vault file from the example:
   - `cp inventory/vault.example.yaml inventory/vault.yaml`
4. Enable local hooks:
   - `pre-commit install`
5. Run all local checks before opening a PR:
   - `pre-commit run --all-files`

## Short issue list (GitHub issue text)

### P0: Add GitHub Actions parity for existing local quality gates

**Problem**
Local quality gates exist via pre-commit, but CI parity is not yet present in this repository.

**Proposal**
Add GitHub Actions to mirror local checks: `ansible-lint`, `yamllint`, `ansible-inventory --list`, and syntax-check of every playbook.

**Done when**
- Checks run on every pull request in GitHub Actions.
- Same checks remain runnable locally with pre-commit.

---

### P1: Add simulation inventory and validation playbook for lab-first changes

**Problem**
Current workflow is oriented to live devices, which increases risk when iterating on VLAN/firewall behavior.

**Proposal**
Add `inventory/hosts.sim.yaml`, `inventory/network.sim.yaml`, `inventory/vault.sim.example.yaml`, and a validation playbook using `ansible.builtin.raw` output parsing for expected topology behavior.

**Done when**
- Operators can run simulation checks without touching production devices.
- Validation asserts expected DHCP/SSID/VLAN behavior.

---

### P1: Add preflight checks for device identity and transport readiness

**Problem**
Plays can begin applying config before confirming expected model/firmware/SSH readiness.

**Proposal**
Add role-level preflight assertions and connection probes before risky tasks.

**Done when**
- Plays fail early if target identity/firmware preconditions are not met.
- Preflight output clearly states reason for fail.

---

### P1: Improve rollback guardrails for gateway VLAN/firewall changes

**Problem**
Gateway-side VLAN/firewall updates can cause remote lockout without an automatic rollback timer.

**Proposal**
Add timed rollback pattern for risky gateway changes and document recovery steps.

**Done when**
- Risky changes include rollback timer + cancel-on-success flow.
- Docs include explicit operator recovery path.

---

### P2: Document and validate `inventory/network.yaml` schema

**Problem**
Shared variable schema is implied but not explicitly validated at run start.

**Proposal**
Document required keys and use `ansible.builtin.assert` for mandatory fields in role preflight.

**Done when**
- Schema doc exists and is linked from runbook docs.
- Missing required keys fail fast with actionable messages.
