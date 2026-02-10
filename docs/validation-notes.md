# Validation Notes

This repository now codifies the README network intent directly in Ansible tasks and in executable checks under `tests/`.

## What was aligned

- Flint 2 gateway baseline now includes:
  - management IP (`10.1.0.1/24`),
  - routed VLAN interfaces (`10`, `20`, `30`, `99`) on `br-lan.<vlan>`,
  - DHCP scopes for each routed VLAN,
  - firewall zones and forwarding rules,
  - specific trusted-to-servers management rule for TCP `22/80/443`.

- Flint 3 AP baseline now includes:
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
