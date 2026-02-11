import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
ROUTER_GARAGE_PLAYBOOK = (ROOT / "ansible-meerkat" / "playbooks" / "router_garage.yml").read_text(encoding="utf-8")
ROUTER_OFFICE_PLAYBOOK = (ROOT / "ansible-meerkat" / "playbooks" / "router_office_ap.yml").read_text(encoding="utf-8")
ROUTER_OFFICE_WITH_TAILSCALE_PLAYBOOK = (ROOT / "ansible-meerkat" / "playbooks" / "router_office_ap_with_tailscale.yml").read_text(encoding="utf-8")
ROUTER_GARAGE_WRAPPER = (ROOT / "ansible-meerkat" / "setup_router_garage.yml").read_text(encoding="utf-8")
ROUTER_OFFICE_WRAPPER = (ROOT / "ansible-meerkat" / "setup_router_office_ap.yml").read_text(encoding="utf-8")
GARAGE_DEFAULTS = (ROOT / "ansible-meerkat" / "roles" / "router_garage" / "defaults" / "main.yml").read_text(encoding="utf-8")
OFFICE_DEFAULTS = (ROOT / "ansible-meerkat" / "roles" / "router_office_ap" / "defaults" / "main.yml").read_text(encoding="utf-8")
TAILSCALE_ROLE_TASKS = (ROOT / "ansible-meerkat" / "roles" / "tailscale_openwrt" / "tasks" / "main.yml").read_text(encoding="utf-8")
TAILSCALE_ROLE_DEFAULTS = (ROOT / "ansible-meerkat" / "roles" / "tailscale_openwrt" / "defaults" / "main.yml").read_text(encoding="utf-8")
ADGUARD_ROLE_TASKS = (ROOT / "ansible-meerkat" / "roles" / "adguard_home_openwrt" / "tasks" / "main.yml").read_text(encoding="utf-8")
ADGUARD_ROLE_DEFAULTS = (ROOT / "ansible-meerkat" / "roles" / "adguard_home_openwrt" / "defaults" / "main.yml").read_text(encoding="utf-8")
WIREGUARD_ROLE_TASKS = (ROOT / "ansible-meerkat" / "roles" / "wireguard_policy_openwrt" / "tasks" / "main.yml").read_text(encoding="utf-8")
WIREGUARD_ROLE_DEFAULTS = (ROOT / "ansible-meerkat" / "roles" / "wireguard_policy_openwrt" / "defaults" / "main.yml").read_text(encoding="utf-8")
GARAGE_TASKS = "\n".join(
    (ROOT / "ansible-meerkat" / "roles" / "router_garage" / "tasks" / name).read_text(encoding="utf-8")
    for name in [
        "main.yml",
        "policy_and_validation.yml",
        "core_network.yml",
        "test_mode_checks.yml",
        "radio_policy.yml",
    ]
)
ROUTER_OFFICE = (ROOT / "ansible-meerkat" / "roles" / "router_office_ap" / "tasks" / "main.yml").read_text(encoding="utf-8")
NETWORK_VARS = (ROOT / "ansible-meerkat" / "group_vars" / "all" / "network.yml").read_text(encoding="utf-8")
INVENTORY = (ROOT / "ansible-meerkat" / "inventory.ini").read_text(encoding="utf-8")


class TestReadmeAlignment(unittest.TestCase):
    def test_vlan_schema_present_in_readme(self):
        for vlan_id, subnet in [(1, "10.1.0.0/24"), (10, "10.10.0.0/24"), (20, "10.20.0.0/24"), (30, "10.30.0.0/24"), (99, "10.99.0.0/24")]:
            self.assertIn(f"**{vlan_id}**", README)
            self.assertIn(subnet, README)

    def test_role_based_project_structure_is_documented(self):
        self.assertIn("Project structure (standardised role layout)", README)
        self.assertIn("ansible-meerkat/playbooks/router_garage.yml", README)
        self.assertIn("ansible-meerkat/playbooks/router_office_ap.yml", README)
        self.assertIn("ansible-meerkat/playbooks/router_office_ap_with_tailscale.yml", README)
        self.assertIn("router_garage/", README)
        self.assertIn("router_office_ap/", README)
        self.assertIn("tailscale_openwrt/", README)

    def test_gateway_vlan_interfaces_declared(self):
        self.assertIn("network.vlan{{ vlan.id }}", GARAGE_TASKS)
        self.assertIn("br-lan.{{ vlan.id }}", GARAGE_TASKS)

    def test_gateway_firewall_zones_and_rules(self):
        self.assertIn("firewall.{{ vlan.zone }}", GARAGE_TASKS)
        self.assertIn("trusted_to_servers_mgmt", GARAGE_TASKS)
        self.assertIn("dest_port='22 80 443'", GARAGE_TASKS)

    def test_ap_static_address_and_dhcp_off(self):
        self.assertIn("10.1.0.4", OFFICE_DEFAULTS)
        self.assertIn("dhcp.lan.ignore='1'", ROUTER_OFFICE)

    def test_ap_ssid_vlan_mapping_matches_readme(self):
        for ssid in ("Meerkat Manor", "Meerkat IoT", "Meerkat Guest"):
            self.assertIn(ssid, README)
            self.assertIn(ssid, NETWORK_VARS)

        patterns = {
            "Meerkat Manor": "vlan_id: 20",
            "Meerkat IoT": "vlan_id: 30",
            "Meerkat Guest": "vlan_id: 99",
        }
        for ssid, vlan_line in patterns.items():
            block = re.search(rf"ssid: '{re.escape(ssid)}'[\s\S]*?(?=\n\s*- name:|\Z)", NETWORK_VARS)
            self.assertIsNotNone(block)
            self.assertIn(vlan_line, block.group(0))

    def test_wifi_keys_are_vault_references(self):
        self.assertIn("{{ vault_wifi_key_manor }}", NETWORK_VARS)
        self.assertIn("{{ vault_wifi_key_iot }}", NETWORK_VARS)
        self.assertIn("{{ vault_wifi_key_guest }}", NETWORK_VARS)

    def test_inventory_uses_router_role_names(self):
        self.assertIn("router-garage", INVENTORY)
        self.assertIn("router-office", INVENTORY)

    def test_playbooks_use_components_and_wrappers_are_kept(self):
        self.assertIn("import_playbook: components/router_garage_core.yml", ROUTER_GARAGE_PLAYBOOK)
        self.assertIn("import_playbook: components/router_garage_tailscale.yml", ROUTER_GARAGE_PLAYBOOK)
        self.assertIn("import_playbook: components/router_office_ap_core.yml", ROUTER_OFFICE_PLAYBOOK)
        self.assertIn("import_playbook: components/router_office_ap_tailscale.yml", ROUTER_OFFICE_WITH_TAILSCALE_PLAYBOOK)
        self.assertIn("import_playbook: playbooks/router_garage.yml", ROUTER_GARAGE_WRAPPER)
        self.assertIn("import_playbook: playbooks/router_office_ap.yml", ROUTER_OFFICE_WRAPPER)

    def test_garage_wifi_policy_is_explicit(self):
        self.assertIn("garage_mgmt_ssid: 'homelab_garage_mngmt'", NETWORK_VARS)
        self.assertIn("garage_test_mode:", NETWORK_VARS)
        self.assertIn("garage_test_repeater_network: 'wwan'", NETWORK_VARS)
        self.assertIn("garage_test_repeater_radio: 'radio1'", NETWORK_VARS)
        self.assertIn("garage_test_repeater_encryption: 'sae'", NETWORK_VARS)
        self.assertIn("garage_test_repeater_radios:", NETWORK_VARS)
        self.assertIn("garage_test_repeater_encryptions:", NETWORK_VARS)
        self.assertIn("garage_test_tailscale_hosts:", NETWORK_VARS)
        self.assertIn("garage_test_uplink_wait_seconds:", NETWORK_VARS)
        self.assertIn("garage_test_uplink_poll_interval_seconds:", NETWORK_VARS)
        self.assertIn("wireless.@wifi-iface[$idx].ssid='{{ garage_mgmt_ssid_effective }}'", GARAGE_TASKS)
        self.assertIn("uci set wireless.sta='wifi-iface'", GARAGE_TASKS)

    def test_tailscale_role_is_generic_and_reusable(self):
        self.assertIn("tailscale_hostname_default", TAILSCALE_ROLE_DEFAULTS)
        self.assertIn("tailscale_advertise_exit_node_default: false", TAILSCALE_ROLE_DEFAULTS)
        self.assertIn("tailscale up", TAILSCALE_ROLE_TASKS)
        self.assertIn("--hostname='{{ tailscale_hostname_effective }}'", TAILSCALE_ROLE_TASKS)
        self.assertIn("--advertise-exit-node", TAILSCALE_ROLE_TASKS)
        self.assertIn("--advertise-routes='{{ tailscale_advertise_routes_csv }}'", TAILSCALE_ROLE_TASKS)
        self.assertIn("https://api.tailscale.com/api/v2/oauth/token", TAILSCALE_ROLE_TASKS)
        self.assertIn("https://api.tailscale.com/api/v2/tailnet/{{ tailscale_oauth_tailnet_effective }}/keys", TAILSCALE_ROLE_TASKS)
        self.assertIn("tailscale_advertise_routes:", NETWORK_VARS)
        self.assertIn("tailscale_oauth_tags:", NETWORK_VARS)

    def test_optional_adguard_and_wireguard_components_are_wired(self):
        self.assertIn("import_playbook: components/router_garage_adguard.yml", ROUTER_GARAGE_PLAYBOOK)
        self.assertIn("import_playbook: components/router_garage_wireguard.yml", ROUTER_GARAGE_PLAYBOOK)
        self.assertIn("adguard_enable: false", NETWORK_VARS)
        self.assertIn("wireguard_policy_enable: false", NETWORK_VARS)
        self.assertIn("adguard_enable_default: false", ADGUARD_ROLE_DEFAULTS)
        self.assertIn("wireguard_policy_enable_default: false", WIREGUARD_ROLE_DEFAULTS)
        self.assertIn("AdGuardHome.yaml", ADGUARD_ROLE_TASKS)
        self.assertIn("vpn-policy-routing", WIREGUARD_ROLE_TASKS)

    def test_garage_wan_pppoe_policy(self):
        self.assertIn("garage_wan_proto: 'pppoe'", NETWORK_VARS)
        self.assertIn("garage_wan_vlan_tag: '911'", NETWORK_VARS)
        self.assertIn("garage_wan_proto_default: \"pppoe\"", GARAGE_DEFAULTS)
        self.assertIn("not (garage_test_mode_effective | bool)", GARAGE_TASKS)
        self.assertIn("PPPoE WAN configuration is skipped", README)
        self.assertIn("vault_garage_wan_pppoe_username", README)
        self.assertIn("vault_garage_wan_pppoe_password", README)


if __name__ == "__main__":
    unittest.main()
