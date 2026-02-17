# How to Backhaul VLANs to the AP-repeater

Use this guide when `gateway-router` (GL.iNet Flint 2) routes VLANs and `ap-repeater` (GL.iNet Beryl) broadcasts per-VLAN SSIDs.

## Goal

- Gateway does routing, DHCP, and firewall for VLANs.
- AP-repeater bridges each SSID to its VLAN.
- AP acts as bridge/AP only (no NAT, no DHCP).
- DHCP should remain disabled on the AP; gateway DHCP serves each VLAN subnet.

## Required cabling model

Preferred:

1. Gateway LAN trunk port -> managed switch trunk port.
2. Managed switch trunk port -> AP uplink port.

If an unmanaged switch is in the path:

- Tagged frames may pass through, but behavior is vendor-dependent and not configurable.
- Every port effectively receives the same tagged traffic, so this is not a safe design for mixed client ports.
- Use unmanaged only for temporary testing, or isolate it to AP backhaul only.

## AP uplink port choice

Use a LAN bridge uplink if your firmware supports it cleanly. In this repository, the AP role disables `network.wan` and uses `br-lan.<vlan-id>` devices for SSID bridge mapping, so the AP is treated as a bridge endpoint rather than a routed WAN client.

## Inventory expectations

This repository already models the required VLAN + SSID mapping in `inventory/network.yaml`:

- VLAN IDs/subnets under `network.vlans`.
- SSID-to-VLAN binding under `network.ap_repeater.ssids` (`vlan_id` per SSID).
- Current topology intent: AP trunk carries VLAN 20/30/40/50/99 as tagged and uses no native VLAN; VLAN 10 is server-only and not broadcast on AP SSIDs.

Management IPs should remain in the management subnet (example):

- Gateway: `10.99.0.1`
- AP-repeater: `10.99.0.3`

## Apply configuration

1. Configure gateway first:

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/gateway-core.yaml -e ansible_host=192.168.8.1
```

2. Configure AP:

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/ap-repeater.yaml
```

## Notes on automation in this repository

- Gateway and AP roles now enable `br-lan` VLAN filtering and build `network.@bridge-vlan` entries so tagged VLAN traffic can traverse the Ethernet backhaul.
- VLAN interfaces remain mapped to `br-lan.<vlan-id>` on gateway and AP.

## Validate

On AP (`ap-repeater`), verify SSIDs map to VLAN bridge interfaces:

```sh
uci show wireless | sed -n '/=wifi-iface/p'
uci show network | sed -n '/ap_vlan/p'
bridge vlan show
```

On gateway (`gateway-router`), verify VLAN interfaces and DHCP pools:

```sh
uci show network | sed -n '/vlan[0-9]\+=interface/p'
uci show dhcp | sed -n '/vlan[0-9]\+=dhcp/p'
```

Client checks:

- Connect each SSID and confirm gateway-issued IP in expected subnet.
- Confirm guest SSID clients get guest subnet addresses and cannot initiate access to trusted/server VLANs.


## SSID naming convention

Use a short family prefix plus network label:

- AP trusted VLAN (20): `Meerkat Manor`
- AP IoT VLAN (30): `MM_IOT`
- AP guest VLAN (40): `Meerkat Manor Guest`
- AP TV VLAN (50): `MM_TV`
- Gateway management SSID: `MM_MGMT`

These are defined in `inventory/network.yaml` and can be adjusted per environment.

## Gateway management Wi-Fi password and side-switch toggle

- Management Wi-Fi password is sourced from `vault_gateway_router_mgmt_password` in `inventory/vault.yaml` (template provided in `inventory/vault.example.yaml`).
- On Flint hardware, side-switch hooks are installed at `/etc/rc.button/BTN_2`, `/etc/rc.button/switch`, and `/etc/rc.button/sw1` to toggle management SSID radios on button press.
- The toggle works in both test mode and production mode because it directly flips `wireless.@wifi-iface[*].disabled` for the management SSID.
