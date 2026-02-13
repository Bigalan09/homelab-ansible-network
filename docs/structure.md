# Repository Structure

```text
.
├── ansible.cfg
├── AGENTS.md
├── adr/
├── dependencies/
│   └── requirements.yaml
├── docs/
│   ├── AGENTS.md
│   ├── structure.md
│   └── how-to/
├── inventory/
│   ├── hosts.yaml
│   ├── network.yaml
│   ├── vault.example.yaml
│   └── vault-pass.enc
├── playbooks/
│   ├── gateway-core.yaml
│   ├── gateway-router.yaml
│   ├── ap-repeater.yaml
│   ├── tailscale.yaml
│   ├── tailscale-nodes.yaml
│   ├── adguard.yaml
│   ├── wireguard-policy.yaml
│   └── crs310-router-on-stick.yaml
├── roles/
│   ├── gateway_router/
│   ├── ap_repeater/
│   ├── tailscale_openwrt/
│   ├── adguard_home_openwrt/
│   ├── wireguard_policy_openwrt/
│   └── mikrotik_crs310_bridge_vlan/
└── scripts/
    ├── vault-pass-encrypt.sh
    └── vault-pass-decrypt.sh
```

## Conventions

- Ansible artifacts use `.yaml` (`ansible.cfg` is the intentional exception).
- Use `ansible.builtin.raw` on managed OpenWrt targets unless Python is guaranteed.
- Inventory belongs in `inventory/*.yaml`.
- Playbooks belong in `playbooks/*.yaml`.
- Roles follow `roles/<role>/{defaults,tasks,vars}/main.yaml`.
