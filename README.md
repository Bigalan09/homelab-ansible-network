# Homelab Ansible Network

Minimal Ansible repo for a two-node OpenWrt setup:
- `gateway-router` (routing, VLANs, optional services)
- `ap-repeater` (VLAN SSID bridge)

## Quick start

```bash
ansible-galaxy collection install -r dependencies/requirements.yaml
cp inventory/vault.example.yaml inventory/vault.yaml
export VAULT_PASS_DECRYPT_KEY='REPLACE_WITH_LOCAL_DECRYPT_KEY'
./scripts/vault-pass-encrypt.sh
ansible-playbook -i inventory/hosts.yaml playbooks/gateway-core.yaml -e ansible_host=192.168.8.1
ansible-playbook -i inventory/hosts.yaml playbooks/ap-repeater.yaml
```

## Docs

- `docs/structure.md`
- `docs/how-to/run-playbooks.md`
- `docs/how-to/gateway-router-ap-repeater-vlan-backhaul.md`
- `docs/how-to/garage-office-topology.md`
- `docs/how-to/repo-survey-and-quality-gates.md`
- `adr/README.md`
