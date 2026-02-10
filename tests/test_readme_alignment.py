import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
FLINT2 = (ROOT / "ansible-meerkat" / "setup_flint2.yml").read_text(encoding="utf-8")
FLINT3 = (ROOT / "ansible-meerkat" / "setup_flint3_ap.yml").read_text(encoding="utf-8")
VARS = (ROOT / "ansible-meerkat" / "group_vars" / "all" / "vault.yml").read_text(encoding="utf-8")


class TestReadmeAlignment(unittest.TestCase):
    def test_vlan_schema_present_in_readme(self):
        for vlan_id, subnet in [(1, "10.1.0.0/24"), (10, "10.10.0.0/24"), (20, "10.20.0.0/24"), (30, "10.30.0.0/24"), (99, "10.99.0.0/24")]:
            self.assertIn(f"**{vlan_id}**", README)
            self.assertIn(subnet, README)

    def test_gateway_vlan_interfaces_declared(self):
        self.assertIn("network.vlan{{ vlan.id }}", FLINT2)
        self.assertIn("br-lan.{{ vlan.id }}", FLINT2)

    def test_gateway_firewall_zones_and_rules(self):
        self.assertIn("firewall.{{ vlan.zone }}", FLINT2)
        self.assertIn("trusted_to_servers_mgmt", FLINT2)
        self.assertIn("dest_port='22 80 443'", FLINT2)

    def test_ap_static_address_and_dhcp_off(self):
        self.assertIn("10.1.0.4", FLINT3)
        self.assertIn("dhcp.lan.ignore='1'", FLINT3)

    def test_ap_ssid_vlan_mapping_matches_readme(self):
        # README SSIDs
        for ssid in ("Meerkat Manor", "Meerkat IoT", "Meerkat Guest"):
            self.assertIn(ssid, README)
            self.assertIn(ssid, VARS)

        # Ensure SSID VLAN mappings requested in README exist in vars.
        patterns = {
            "Meerkat Manor": "vlan_id: 20",
            "Meerkat IoT": "vlan_id: 30",
            "Meerkat Guest": "vlan_id: 99",
        }
        for ssid, vlan_line in patterns.items():
            block = re.search(rf"ssid: '{re.escape(ssid)}'[\s\S]*?(?=\n\s*- name:|\Z)", VARS)
            self.assertIsNotNone(block)
            self.assertIn(vlan_line, block.group(0))


if __name__ == "__main__":
    unittest.main()
