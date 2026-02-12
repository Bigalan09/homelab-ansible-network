# Homelab Ansible Network

This repository is structured for consistent Ansible operations with:
- one inventory directory,
- one dependencies directory,
- simple playbook names,
- role directories with `defaults/`, `tasks/`, and `vars/`,
- documentation split into focused docs,
- ADRs to capture architectural decisions.

## Quick start

1. Install dependencies:
   ```bash
   ansible-galaxy collection install -r dependencies/requirements.yaml
   ```
2. Edit non-secrets in `inventory/network.yaml`.
3. Start from `inventory/vault.example.yaml`, then edit secrets with Ansible Vault in `inventory/vault.yaml`.
4. Run playbooks from `playbooks/` (staged core-first recommended):
   ```bash
   cp inventory/vault.example.yaml inventory/vault.yaml
   export VAULT_PASS_DECRYPT_KEY='REPLACE_WITH_LOCAL_DECRYPT_KEY'
   ./scripts/vault-pass-encrypt.sh
   ansible-playbook -i inventory/hosts.yaml playbooks/gateway-core.yaml -e ansible_host=192.168.8.1
   ansible-playbook -i inventory/hosts.yaml playbooks/tailscale.yaml -e tailscale_enable=true
   ansible-playbook -i inventory/hosts.yaml playbooks/adguard.yaml -e adguard_enable=true
   ansible-playbook -i inventory/hosts.yaml playbooks/ap.yaml
   ```

Encrypted vault password helper:
- Encrypted vault password file: `inventory/vault-pass.enc`
- Encrypt/update helper: `scripts/vault-pass-encrypt.sh`
- Decrypt helper for Ansible: `scripts/vault-pass-decrypt.sh`
- `VAULT_PASS_DECRYPT_KEY` must be exported in your shell before running Ansible.
- `ansible.cfg` sets `vault_password_file = ./scripts/vault-pass-decrypt.sh` by default.
- Repo bootstrap file `inventory/vault-pass.enc` is a placeholder and should be replaced locally.

## Documentation index

- Structure guide: `docs/structure.md`
- How-to guides: `docs/how-to/`
- Topology notes: `docs/topology/overview.md`
- Validation notes: `docs/validation-notes.md`
- ADR index: `adr/README.md`
