# ADR 0005: Management VLAN 99 as a routed VLAN with tagged trunks

## Context

The previous design kept management VLAN 99 as an untagged native VLAN on
all bridge ports and trunk links. This conflicted with the security principle
of "no native VLANs on trunk ports" and prevented explicit firewall policy
for the management network.

The target network topology requires:

- VLAN 99 tagged on all trunk ports (MT6000 ↔ CRS310, CRS310 ↔ MT3000),
- VLAN 99 untagged only on a dedicated management access port (MT6000 last LAN port),
- VLAN 99 with its own routed interface (10.99.0.0/24, gateway 10.99.0.1),
- DHCP and firewall zone for management traffic,
- MT6000 gateway SSIDs (MM_TV, MM_SRV, MM_MGMT) on per-VLAN interfaces,
- AP SSID names aligned to the design (MM_IOT, Meerkat Manor Guest, MM_TV),
- CRS310 ether3 as an access port for VLAN 10 (Servers).

## Decision

- Add VLAN 99 to `network.vlans` with `name: management`, `ip: 10.99.0.1`,
  and `zone: mgmt_zone`.
- Change gateway LAN IP from `10.1.0.1` to `10.99.0.1`.
- Change AP management IP from `10.1.0.4` to `10.99.0.3`.
- Change CRS310 management IP from `10.1.0.2/24` to `10.99.0.2/24`.
- Set CRS310 `trunk_native_pvid` to `1` (no usable native VLAN on trunks).
- Tag VLAN 99 on CRS310 ether1 and ether2 trunk ports.
- Remove untagged VLAN 99 membership from trunk ports.
- Update `gateway_router` role to:
  - treat VLAN 99 as a routed VLAN with interface, DHCP, and firewall zone,
  - accept a `mgmt_access_port` setting to identify the untagged management port,
  - tag VLAN 99 on all other bridge ports (trunk behaviour),
  - create per-VLAN SSID mappings from `network.gateway_router.ssids`.
- Update firewall forwarding rules to include `mgmt_zone → all` and
  `trusted_zone → iot_zone / tv_zone`.
- Fix AP SSID names and CRS310 ether3 access VLAN to match the design.
- Replace the assertion that prohibited VLAN 99 in the VLANs list with one
  that requires it.

## Consequences

- Management network is now explicitly routed, firewalled, and DHCP-served.
- Trunk ports carry only tagged frames; no implicit native VLAN leakage.
- Dedicated management access port provides physical security control.
- Gateway router can broadcast per-VLAN SSIDs (MM_TV, MM_SRV) alongside
  the management SSID (MM_MGMT) controlled by the physical Wi-Fi switch.
- Existing deployments must update their management IP addressing
  (10.1.0.x → 10.99.0.x) before applying.

## Related

- `inventory/network.yaml`
- `inventory/hosts.yaml`
- `roles/gateway_router/defaults/main.yaml`
- `roles/gateway_router/tasks/core_network.yaml`
- `roles/gateway_router/tasks/policy_and_validation.yaml`
- `roles/ap_repeater/defaults/main.yaml`
- `roles/mikrotik_crs310_bridge_vlan/defaults/main.yaml`
