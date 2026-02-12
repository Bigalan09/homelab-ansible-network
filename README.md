# Homelab Ansible Network

This repository is structured for consistent Ansible operations with:
- one inventory directory,
- one dependencies directory,
- simple playbook names,
- role directories with `default/`, `tasks/`, and `vars/`,
- documentation split into focused docs,
- ADRs to capture architectural decisions.

## Quick start

1. Install dependencies:
   ```bash
   ansible-galaxy collection install -r dependencies/requirements.yaml
   ```
2. Edit non-secrets in `inventory/network.yaml`.
3. Edit secrets with Ansible Vault in `inventory/vault.yaml`.
4. Run playbooks from `playbooks/`:
   ```bash
   ansible-playbook -i inventory/hosts.yaml playbooks/gateway-router.yaml --ask-vault-pass
   ansible-playbook -i inventory/hosts.yaml playbooks/ap.yaml --ask-vault-pass
   ```

## Documentation index

- Structure guide: `docs/structure.md`
- How-to guides: `docs/how-to/`
- Topology notes: `docs/topology/overview.md`
- Validation notes: `docs/validation-notes.md`
- ADR index: `adr/README.md`
