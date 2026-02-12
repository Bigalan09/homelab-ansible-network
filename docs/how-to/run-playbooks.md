# How to Run Playbooks

## Gateway router

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/gateway-router.yaml --ask-vault-pass
```

## Access point

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/ap.yaml --ask-vault-pass
```

## Service-only runs

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/tailscale.yaml --ask-vault-pass
ansible-playbook -i inventory/hosts.yaml playbooks/adguard.yaml --ask-vault-pass
ansible-playbook -i inventory/hosts.yaml playbooks/wireguard-policy.yaml --ask-vault-pass
```
