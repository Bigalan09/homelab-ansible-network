# ADR 0004: Use CRS310 as VLAN distribution core with management VLAN 99

## Context

The homelab now includes a managed MikroTik CRS310 in the garage rack, plus multiple unmanaged downstream switches and an office AP uplink. The previous switch role assumed a single access VLAN across all access ports and did not consume `network.mikrotik_crs310` inventory settings.

The target topology requires:

- routed VLANs on the gateway (`10/20/30/40/50`),
- management network on VLAN `99`,
- AP trunk carrying `20/30/40/50` (no VLAN `10` SSID backhaul),
- per-port access VLAN assignment on CRS310 (including SFP+ ports).

## Decision

- Keep routing/DHCP/firewall/VPN policy on `gateway-router`.
- Use CRS310 as the L2 VLAN distribution core.
- Standardize management VLAN on `99` for gateway/AP trunk native VLAN behavior.
  *(Superseded by ADR 0005: VLAN 99 is now tagged on trunks with no native VLAN.)*
- Update `mikrotik_crs310_bridge_vlan` role to:
  - resolve settings from `network.mikrotik_crs310`,
  - configure trunk native PVID for uplink/AP ports,
  - configure per-port access PVID mappings,
  - manage bridge VLAN entries with both tagged and untagged memberships.
- Update inventory topology and AP SSID mappings so AP serves VLANs `20/30/40/50` only.

## Consequences

- CRS310 can now express mixed access/trunk behavior required by rack and office cabling.
- VLAN intent is explicit in inventory for both tagged and untagged port membership.
- Unmanaged switches remain single-VLAN access segments only.
- Existing deployments relying on the old CRS310 defaults should verify or override inventory settings before apply.

## Related

- `inventory/network.yaml`
- `roles/mikrotik_crs310_bridge_vlan/defaults/main.yaml`
- `roles/mikrotik_crs310_bridge_vlan/tasks/main.yaml`
- `roles/gateway_router/defaults/main.yaml`
- `roles/ap_repeater/defaults/main.yaml`
- `docs/how-to/garage-office-topology.md`
