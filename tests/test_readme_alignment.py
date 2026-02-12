import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
STRUCTURE_DOC = (ROOT / "docs" / "structure.md").read_text(encoding="utf-8")
INVENTORY = (ROOT / "inventory" / "hosts.yaml").read_text(encoding="utf-8")
NETWORK = (ROOT / "inventory" / "network.yaml").read_text(encoding="utf-8")
GATEWAY_PLAYBOOK = (ROOT / "playbooks" / "gateway-router.yaml").read_text(encoding="utf-8")
GATEWAY_CORE_PLAYBOOK = (ROOT / "playbooks" / "gateway-core.yaml").read_text(encoding="utf-8")
AP_PLAYBOOK = (ROOT / "playbooks" / "ap.yaml").read_text(encoding="utf-8")
TAILSCALE_NODES_PLAYBOOK = (ROOT / "playbooks" / "tailscale-nodes.yaml").read_text(encoding="utf-8")


class TestRepoLayout(unittest.TestCase):
    def test_required_top_level_layout_exists(self):
        for path in [
            "dependencies/requirements.yaml",
            "inventory/hosts.yaml",
            "inventory/network.yaml",
            "inventory/vault-pass.enc",
            "inventory/vault.example.yaml",
            "inventory/vault.yaml",
            "playbooks/gateway-core.yaml",
            "playbooks/gateway-router.yaml",
            "playbooks/ap.yaml",
            "playbooks/tailscale.yaml",
            "playbooks/tailscale-nodes.yaml",
            "playbooks/adguard.yaml",
            "playbooks/wireguard-policy.yaml",
            "scripts/vault-pass-encrypt.sh",
            "scripts/vault-pass-decrypt.sh",
            "roles/router_garage/defaults/main.yaml",
            "roles/router_garage/tasks/main.yaml",
            "roles/router_garage/vars/main.yaml",
            "ansible.cfg",
            ".ansible-lint.yaml",
            "AGENTS.md",
            "AI.md",
            "adr/0001-standardize-layout.md",
        ]:
            self.assertTrue((ROOT / path).exists(), path)

    def test_inventory_and_network_are_yaml_hierarchical(self):
        self.assertIn("router-garage", INVENTORY)
        self.assertIn("router-office", INVENTORY)
        self.assertIn("openwrt_tailscale_nodes", INVENTORY)
        self.assertIn("network:", NETWORK)
        self.assertIn("services:", NETWORK)

    def test_playbooks_use_new_paths(self):
        self.assertIn("../inventory/network.yaml", GATEWAY_PLAYBOOK)
        self.assertIn("../inventory/vault.yaml", GATEWAY_PLAYBOOK)
        self.assertIn("router_garage", GATEWAY_CORE_PLAYBOOK)
        self.assertIn("openwrt_tailscale_nodes", TAILSCALE_NODES_PLAYBOOK)
        self.assertIn("roles:", AP_PLAYBOOK)

    def test_docs_point_to_split_structure(self):
        self.assertIn("docs/structure.md", README)
        self.assertIn("docs/how-to/", README)
        self.assertIn("adr/README.md", README)
        self.assertIn("vault-pass-decrypt.sh", README)
        self.assertIn("roles/<role>/{defaults,tasks,vars}", STRUCTURE_DOC)


if __name__ == "__main__":
    unittest.main()
