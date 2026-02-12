# Repository Structure

```text
.
├── .ansible-lint.yaml
├── AGENTS.md
├── AI.md
├── dependencies/
│   └── requirements.yaml
├── inventory/
│   ├── hosts.yaml
│   ├── network.yaml
│   └── vault.yaml
├── playbooks/
│   ├── gateway-router.yaml
│   ├── ap.yaml
│   ├── tailscale.yaml
│   ├── adguard.yaml
│   └── wireguard-policy.yaml
├── roles/
│   ├── router_garage/
│   │   ├── default/main.yaml
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

- Role pattern: `roles/<role>/{default,tasks,vars}/main.yaml`
