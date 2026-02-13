# How to Backhaul VLANs to the Office AP

Use this guide when `router-garage` (GL.iNet Flint 2) routes VLANs and `router-office` (GL.iNet Beryl) broadcasts per-VLAN SSIDs.

## Goal

- Gateway does routing, DHCP, and firewall for VLANs.
- Office AP bridges each SSID to its VLAN.
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
- SSID-to-VLAN binding under `network.office_ap.ssids` (`vlan_id` per SSID).

Management IPs should remain in the management subnet (example):

- Gateway: `10.1.0.1`
- Office AP: `10.1.0.4`

## Apply configuration

1. Configure gateway first:

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/gateway-core.yaml -e ansible_host=192.168.8.1
```

2. Configure AP:

```bash
ansible-playbook -i inventory/hosts.yaml playbooks/ap.yaml
```

## Notes on automation in this repository

- Gateway and AP roles now enable `br-lan` VLAN filtering and build `network.@bridge-vlan` entries so tagged VLAN traffic can traverse the Ethernet backhaul.
- VLAN interfaces remain mapped to `br-lan.<vlan-id>` on gateway and AP.

## Validate

On AP (`router-office`), verify SSIDs map to VLAN bridge interfaces:

```sh
uci show wireless | sed -n '/=wifi-iface/p'
uci show network | sed -n '/ap_vlan/p'
bridge vlan show
```

On gateway (`router-garage`), verify VLAN interfaces and DHCP pools:

```sh
uci show network | sed -n '/vlan[0-9]\+=interface/p'
uci show dhcp | sed -n '/vlan[0-9]\+=dhcp/p'
```

Client checks:

- Connect each SSID and confirm gateway-issued IP in expected subnet.
- Confirm guest SSID clients get guest subnet addresses and cannot initiate access to trusted/server VLANs.
