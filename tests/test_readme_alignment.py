import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
ROUTER_GARAGE_PLAYBOOK = (ROOT / "ansible-meerkat" / "playbooks" / "router_garage.yml").read_text(encoding="utf-8")
ROUTER_OFFICE_PLAYBOOK = (ROOT / "ansible-meerkat" / "playbooks" / "router_office_ap.yml").read_text(encoding="utf-8")
ROUTER_OFFICE_WITH_TAILSCALE_PLAYBOOK = (ROOT / "ansible-meerkat" / "playbooks" / "router_office_ap_with_tailscale.yml").read_text(encoding="utf-8")
GARAGE_TASKFILE = (ROOT / "ansible-meerkat" / "playbooks" / "tasks" / "router_garage.yml").read_text(encoding="utf-8")
OFFICE_CORE_TASKFILE = (ROOT / "ansible-meerkat" / "playbooks" / "tasks" / "router_office_ap_core.yml").read_text(encoding="utf-8")
OFFICE_TS_TASKFILE = (ROOT / "ansible-meerkat" / "playbooks" / "tasks" / "router_office_ap_tailscale.yml").read_text(encoding="utf-8")
NETWORK_VARS = (ROOT / "ansible-meerkat" / "group_vars" / "all" / "network.yml").read_text(encoding="utf-8")
INVENTORY = (ROOT / "ansible-meerkat" / "inventory.yml").read_text(encoding="utf-8")


class TestReadmeAlignment(unittest.TestCase):
    def test_inventory_yaml_exists_and_uses_router_role_names(self):
        self.assertIn("router-garage", INVENTORY)
        self.assertIn("router-office", INVENTORY)
        self.assertIn("ansible_ssh_common_args", INVENTORY)

    def test_playbooks_use_taskfiles_not_nested_playbooks(self):
        self.assertIn("import_tasks: tasks/router_garage.yml", ROUTER_GARAGE_PLAYBOOK)
        self.assertIn("import_tasks: tasks/router_office_ap_core.yml", ROUTER_OFFICE_PLAYBOOK)
        self.assertIn("import_tasks: tasks/router_office_ap_tailscale.yml", ROUTER_OFFICE_WITH_TAILSCALE_PLAYBOOK)
        self.assertIn("include_role", GARAGE_TASKFILE)
        self.assertIn("include_role", OFFICE_CORE_TASKFILE)
        self.assertIn("include_role", OFFICE_TS_TASKFILE)

    def test_hierarchical_network_config_present(self):
        self.assertIn("network:", NETWORK_VARS)
        self.assertIn("garage:", NETWORK_VARS)
        self.assertIn("office_ap:", NETWORK_VARS)
        self.assertIn("services:", NETWORK_VARS)
        self.assertIn("tailscale:", NETWORK_VARS)
        self.assertIn("wireguard_policy:", NETWORK_VARS)
        self.assertIn("adguard:", NETWORK_VARS)

    def test_readme_references_yaml_inventory(self):
        self.assertIn("ansible-meerkat/inventory.yml", README)
        self.assertNotIn("ansible-meerkat/inventory.ini", README)


if __name__ == "__main__":
    unittest.main()
