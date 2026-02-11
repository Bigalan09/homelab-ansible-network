import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
ROUTER_GARAGE_PLAYBOOK = (ROOT / "ansible-meerkat" / "playbooks" / "router_garage.yml").read_text(encoding="utf-8")
ROUTER_OFFICE_PLAYBOOK = (ROOT / "ansible-meerkat" / "playbooks" / "router_office_ap.yml").read_text(encoding="utf-8")
ROUTER_GARAGE_WRAPPER = (ROOT / "ansible-meerkat" / "setup_router_garage.yml").read_text(encoding="utf-8")
ROUTER_OFFICE_WRAPPER = (ROOT / "ansible-meerkat" / "setup_router_office_ap.yml").read_text(encoding="utf-8")
GARAGE_DEFAULTS = (ROOT / "ansible-meerkat" / "roles" / "router_garage" / "defaults" / "main.yml").read_text(encoding="utf-8")
OFFICE_DEFAULTS = (ROOT / "ansible-meerkat" / "roles" / "router_office_ap" / "defaults" / "main.yml").read_text(encoding="utf-8")
GARAGE_TASKS = "\n".join(
    (ROOT / "ansible-meerkat" / "roles" / "router_garage" / "tasks" / name).read_text(encoding="utf-8")
    for name in [
        "main.yml",
        "policy_and_validation.yml",
        "core_network.yml",
        "test_mode_checks.yml",
        "tailscale.yml",
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
        self.assertIn("router_garage/", README)
        self.assertIn("router_office_ap/", README)

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
        self.assertNotIn("FamilyPass2026", NETWORK_VARS)
        self.assertNotIn("SmartHomeDevices", NETWORK_VARS)
        self.assertNotIn("VisitorPass", NETWORK_VARS)

    def test_inventory_uses_router_role_names(self):
        self.assertIn("router-garage", INVENTORY)
        self.assertIn("router-office", INVENTORY)

    def test_playbooks_use_roles_and_wrappers_are_kept(self):
        self.assertIn("roles:\n    - role: router_garage", ROUTER_GARAGE_PLAYBOOK)
        self.assertIn("roles:\n    - role: router_office_ap", ROUTER_OFFICE_PLAYBOOK)
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
        self.assertIn("uci set wireless.sta.disabled='0'", GARAGE_TASKS)
        self.assertIn("uci -q delete wireless.sta.wds", GARAGE_TASKS)
        self.assertIn("selected_radio='{{ garage_test_repeater_radio_effective }}'", GARAGE_TASKS)
        self.assertIn('iwinfo "$radio" scan', GARAGE_TASKS)
        self.assertIn("Show repeater diagnostics when test-mode uplink check fails", GARAGE_TASKS)
        self.assertIn("Test-mode check: verify repeater uplink internet and tailscale control-plane reachability", GARAGE_TASKS)
        self.assertIn("ifstatus {{ garage_test_repeater_network_effective }}", GARAGE_TASKS)
        self.assertIn("ifup {{ garage_test_repeater_network_effective }}", GARAGE_TASKS)
        self.assertIn("uplink_wait_elapsed_seconds=$elapsed", GARAGE_TASKS)
        self.assertIn("garage_test_uplink_wait_seconds_effective", GARAGE_TASKS)
        self.assertIn("garage_test_uplink_poll_interval_seconds_effective", GARAGE_TASKS)
        self.assertIn("Print repeater diagnostics summary when test-mode uplink check fails", GARAGE_TASKS)
        self.assertIn("uclient-fetch -T 5 -qO- https://{{ host }}", GARAGE_TASKS)
        self.assertIn("No usable wifi-device section found in wireless UCI config.", GARAGE_TASKS)
        self.assertIn('selected_radio="$(uci -q show wireless', GARAGE_TASKS)
        self.assertIn("Configure test-mode repeater password (secret)", GARAGE_TASKS)
        self.assertIn("garage_test_tailscale_ping.rc != 0", GARAGE_TASKS)
        self.assertIn("garage_test_mode is enabled; Wi-Fi radios are kept enabled", GARAGE_TASKS)
        self.assertIn("ifstatus wan", GARAGE_TASKS)
        self.assertIn("garage_wan_internet_check.rc == 0", GARAGE_TASKS)

    def test_garage_reload_handoff_is_best_effort(self):
        self.assertIn('nohup sh -c "sleep 2; /etc/init.d/network reload; wifi reload', GARAGE_TASKS)
        self.assertIn("ansible.builtin.wait_for", GARAGE_TASKS)
        self.assertIn("failed_when: false", GARAGE_TASKS)

    def test_garage_tailscale_exit_node_policy(self):
        self.assertIn("tailscale_enable: true", NETWORK_VARS)
        self.assertIn("tailscale_advertise_routes:", NETWORK_VARS)
        self.assertIn("tailscale_oauth_tailnet: '-'", NETWORK_VARS)
        self.assertIn("tailscale_oauth_tags:", NETWORK_VARS)
        self.assertIn("vault_tailscale_oauth_client_id", README)
        self.assertIn("vault_tailscale_oauth_client_secret", README)
        self.assertIn("tskey-client-...", README)
        self.assertIn("opkg update && opkg install kmod-tun tailscale", GARAGE_TASKS)
        self.assertIn("https://api.tailscale.com/api/v2/oauth/token", GARAGE_TASKS)
        self.assertIn("https://api.tailscale.com/api/v2/tailnet/{{ tailscale_oauth_tailnet_effective }}/keys", GARAGE_TASKS)
        self.assertIn("- 201", GARAGE_TASKS)
        self.assertIn("tailscale_oauth_key_result.status | default(0) in [200, 201]", GARAGE_TASKS)
        self.assertIn("tailscale_auth_key_for_up_effective", GARAGE_TASKS)
        self.assertIn("tailscale_use_oauth_secret_authkey_effective", GARAGE_TASKS)
        self.assertIn("--advertise-tags='{{ tailscale_oauth_tags_csv }}'", GARAGE_TASKS)
        self.assertIn("Show tailscale OAuth token diagnostics (best effort)", GARAGE_TASKS)
        self.assertIn("--advertise-exit-node", GARAGE_TASKS)
        self.assertIn("--advertise-routes='{{ tailscale_advertise_routes_csv }}'", GARAGE_TASKS)
        self.assertIn("(tailscale_up_authkey_result.rc | default(1)) != 0", GARAGE_TASKS)
        self.assertIn("(tailscale_up_oauth_key_result.rc | default(1)) != 0", GARAGE_TASKS)

    def test_garage_wan_pppoe_policy(self):
        self.assertIn("garage_wan_proto: 'pppoe'", NETWORK_VARS)
        self.assertIn("garage_wan_vlan_tag: '911'", NETWORK_VARS)
        self.assertIn("garage_wan_proto_default: \"pppoe\"", GARAGE_DEFAULTS)
        self.assertIn("not (garage_test_mode_effective | bool)", GARAGE_TASKS)
        self.assertIn("PPPoE WAN configuration is skipped", README)
        self.assertIn("vault_garage_wan_pppoe_username", README)
        self.assertIn("vault_garage_wan_pppoe_password", README)
        self.assertIn("VLAN tag: **911**", README)
        self.assertIn("uci set network.wan_vlan='device'", GARAGE_TASKS)
        self.assertIn("uci set network.wan_vlan.vid='{{ garage_wan_vlan_tag_effective }}'", GARAGE_TASKS)
        self.assertIn("uci set network.wan.proto='pppoe'", GARAGE_TASKS)
        self.assertIn('uci set network.wan.device="$wan_vlan_dev"', GARAGE_TASKS)
        self.assertIn("uci set network.wan.username='{{ garage_wan_pppoe_username_effective }}'", GARAGE_TASKS)
        self.assertIn("uci set network.wan.password='{{ garage_wan_pppoe_password_effective }}'", GARAGE_TASKS)


if __name__ == "__main__":
    unittest.main()
