# How to Run Playbooks

## Install required collections

```bash
ansible-galaxy collection install -r dependencies/requirements.yaml
```

## Vault password file workflow (encrypted)

```bash
export VAULT_PASS_DECRYPT_KEY='REPLACE_WITH_LOCAL_DECRYPT_KEY'
./scripts/vault-pass-encrypt.sh
```

Ansible uses `scripts/vault-pass-decrypt.sh` by default via `ansible.cfg`.
Override explicitly only if needed:

```bash
--vault-password-file ./scripts/vault-pass-decrypt.sh
```

## Gateway router (core only, recommended first)

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/gateway-core.yaml -e ansible_host=192.168.8.1
```

## Gateway router (full stack)

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/gateway-router.yaml
```

## Access point

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/ap-repeater.yaml
```

For VLAN trunk/backhaul expectations between gateway and AP, see `docs/how-to/gateway-router-ap-repeater-vlan-backhaul.md`.
For the full garage/office physical topology and port map, see `docs/how-to/garage-office-topology.md`.

## MikroTik CRS310 (Router-on-a-Stick using Bridge VLAN Filtering)

Ensure your switch is in the `switches` inventory group and reachable first.

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/crs310-router-on-stick.yaml
```

The CRS310 role stages bridge VLAN entries first and enables `vlan-filtering` only at the end. It also installs a temporary timed rollback scheduler before the cutover and removes it after success.

## Service-only runs

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/tailscale.yaml
ansible-playbook -i inventory/hosts.yaml playbooks/adguard.yaml
ansible-playbook -i inventory/hosts.yaml playbooks/wireguard-policy.yaml
```

## Reusable OpenWrt tailscale nodes

Add hosts under `openwrt_tailscale_nodes` in `inventory/hosts.yaml`, then run:

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/tailscale-nodes.yaml
```

## Local quality checks (recommended before PRs)

```bash
python -m venv .venv
source .venv/bin/activate
pip install ansible ansible-lint yamllint pre-commit
ansible-galaxy collection install -r dependencies/requirements.yaml
cp inventory/vault.example.yaml inventory/vault.yaml
pre-commit install
pre-commit run --all-files
```

These checks mirror CI quality gates (lint, inventory load, and playbook syntax checks).
