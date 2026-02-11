import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
ROUTER_GARAGE = (ROOT / "ansible-meerkat" / "setup_router_garage.yml").read_text(encoding="utf-8")
ROUTER_OFFICE = (ROOT / "ansible-meerkat" / "setup_router_office_ap.yml").read_text(encoding="utf-8")
NETWORK_VARS = (ROOT / "ansible-meerkat" / "group_vars" / "all" / "network.yml").read_text(encoding="utf-8")
INVENTORY = (ROOT / "ansible-meerkat" / "inventory.ini").read_text(encoding="utf-8")


class TestReadmeAlignment(unittest.TestCase):
    def test_vlan_schema_present_in_readme(self):
        for vlan_id, subnet in [(1, "10.1.0.0/24"), (10, "10.10.0.0/24"), (20, "10.20.0.0/24"), (30, "10.30.0.0/24"), (99, "10.99.0.0/24")]:
            self.assertIn(f"**{vlan_id}**", README)
            self.assertIn(subnet, README)

    def test_gateway_vlan_interfaces_declared(self):
        self.assertIn("network.vlan{{ vlan.id }}", ROUTER_GARAGE)
        self.assertIn("br-lan.{{ vlan.id }}", ROUTER_GARAGE)

    def test_gateway_firewall_zones_and_rules(self):
        self.assertIn("firewall.{{ vlan.zone }}", ROUTER_GARAGE)
        self.assertIn("trusted_to_servers_mgmt", ROUTER_GARAGE)
        self.assertIn("dest_port='22 80 443'", ROUTER_GARAGE)

    def test_ap_static_address_and_dhcp_off(self):
        self.assertIn("10.1.0.4", ROUTER_OFFICE)
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
        self.assertNotIn("FamilyPass2026", NETWORK_VARS)
        self.assertNotIn("SmartHomeDevices", NETWORK_VARS)
        self.assertNotIn("VisitorPass", NETWORK_VARS)

    def test_inventory_uses_router_role_names(self):
        self.assertIn("router-garage", INVENTORY)
        self.assertIn("router-office", INVENTORY)

    def test_garage_wifi_policy_is_explicit(self):
        self.assertIn("garage_mgmt_ssid: 'homelab_garage_mngmt'", NETWORK_VARS)
        self.assertIn("wireless.@wifi-iface[$idx].ssid='{{ garage_mgmt_ssid_effective }}'", ROUTER_GARAGE)
        self.assertIn("wireless.{{ radio }}.disabled='1'", ROUTER_GARAGE)

    def test_garage_reload_handoff_is_best_effort(self):
        self.assertIn("nohup sh -c \"sleep 2; /etc/init.d/network reload; wifi reload", ROUTER_GARAGE)
        self.assertIn("ansible.builtin.wait_for", ROUTER_GARAGE)
        self.assertIn("failed_when: false", ROUTER_GARAGE)


if __name__ == "__main__":
    unittest.main()
