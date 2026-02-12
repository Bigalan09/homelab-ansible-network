# Repository Structure

```text
.
├── ansible.cfg
├── .ansible-lint.yaml
├── AGENTS.md
├── AI.md
├── dependencies/
│   └── requirements.yaml
├── inventory/
│   ├── hosts.yaml
│   ├── network.yaml
│   ├── vault-pass.enc
│   ├── vault.example.yaml
│   └── vault.yaml
├── playbooks/
│   ├── gateway-core.yaml
│   ├── gateway-router.yaml
│   ├── ap.yaml
│   ├── tailscale.yaml
│   ├── tailscale-nodes.yaml
│   ├── adguard.yaml
│   └── wireguard-policy.yaml
├── scripts/
│   ├── vault-pass-encrypt.sh
│   └── vault-pass-decrypt.sh
├── roles/
│   ├── router_garage/
│   │   ├── defaults/main.yaml
│   │   ├── tasks/main.yaml
│   │   └── vars/main.yaml
│   ├── router_office_ap/
│   ├── tailscale_openwrt/
│   ├── adguard_home_openwrt/
│   └── wireguard_policy_openwrt/
├── docs/
│   ├── structure.md
│   ├── how-to/
│   └── topology/
└── adr/
    ├── README.md
    └── 0001-standardize-layout.md
```

## Conventions

- Inventory files are YAML only.
- Playbook names are short and descriptive.
- New architectural decisions must be documented in `adr/`.
- New operational guidance belongs in `docs/how-to/`.

- Role pattern: `roles/<role>/{defaults,tasks,vars}/main.yaml`
