# ADR 0003: Standardize bridge VLAN trunking for gateway and AP backhaul

## Context

The network model in `inventory/network.yaml` defines routed VLANs on the gateway and SSID-to-VLAN mappings on the AP. Previously, roles created `br-lan.<vlan-id>` interfaces but did not explicitly configure `network.@bridge-vlan` membership on `br-lan`.

Without bridge VLAN filtering and per-port tagged membership, VLAN-tagged backhaul traffic can fail between AP and gateway.

## Decision

- `gateway_router` and `ap_repeater` roles will explicitly:
  - enable `vlan_filtering` on `br-lan`,
  - rebuild `network.@bridge-vlan` entries idempotently,
  - keep management/native VLAN untagged on the dedicated management access port,
    tagged on all other bridge member ports (see ADR 0005),
  - mark configured VLANs as tagged on bridge member ports.
- DHCP remains centralized on the gateway; AP remains bridge-only.

## Consequences

- AP SSIDs mapped to VLANs can traverse Ethernet backhaul to the gateway consistently.
- The baseline now depends on DSA bridge VLAN behavior (OpenWrt model), which is expected for these target devices.
- Deployments should verify uplink/backhaul switch behavior, especially when unmanaged switches are used.

## Related

- `roles/gateway_router/tasks/core_network.yaml`
- `roles/ap_repeater/tasks/main.yaml`
- `docs/how-to/gateway-router-ap-repeater-vlan-backhaul.md`
