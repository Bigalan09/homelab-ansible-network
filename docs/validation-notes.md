# Validation Notes

This repository now codifies the README network intent directly in Ansible tasks and in executable checks under `tests/`.

## What was aligned

- Naming is now role-based (`router-garage` and `router-office`) instead of model-based labels.
- Variables are split into:
  - `ansible-meerkat/group_vars/all/network.yml` for non-secrets,
  - `ansible-meerkat/group_vars/all/vault.yml` for secrets (intended for Ansible Vault encryption).

- Router Garage gateway baseline now includes:
  - management IP (`10.1.0.1/24`),
  - WAN configured for PPPoE on VLAN `911` using Vault-provided credentials,
  - routed VLAN interfaces (`10`, `20`, `30`, `99`) on `br-lan.<vlan>`,
  - DHCP scopes for each routed VLAN,
  - firewall zones and forwarding rules,
  - specific trusted-to-servers management rule for TCP `22/80/443`.
  - garage Wi-Fi SSID relabeled to `homelab_garage_mngmt` before radio shutdown,
  - 2.4/5 GHz radios disabled after VLAN/firewall policy is staged.
  - best-effort Tailscale provisioning (install/start + advertise exit node and subnet routes).

- Router Office AP baseline now includes:
  - AP management IP (`10.1.0.4`), gateway and DNS (`10.1.0.1`),
  - DHCP disabled on AP LAN,
  - VLAN backhaul interfaces on `br-lan.<vlan>`,
  - SSID-to-VLAN mappings for Meerkat Manor (20), IoT (30), Guest (99).

## Internet references consulted

- OpenWrt UCI network config examples (interfaces, bridge/VLAN patterns):
  <https://openwrt.org/docs/guide-user/network/ucicheatsheet>
- OpenWrt guest Wi-Fi and firewall-zone design:
  <https://openwrt.org/docs/guide-user/network/wifi/guestwifi/guest-wlan>
- GL.iNet OpenWrt-based docs and admin model:
  <https://docs.gl-inet.com/>

These references were used as implementation patterns while keeping the source of truth for desired state as this repository's README.
