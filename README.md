# Homelab Network Documentation: Meerkat Manor

**Last Updated:** 2026-02-11  
**Location:** UK  
**Gateway Role Host:** `router-garage` (GL.iNet/OpenWrt device in Garage)  
**Office AP Role Host:** `router-office` (GL.iNet/OpenWrt device in Office, currently tested with Beryl MT3000)

---


## 0.0 Project structure (standardised role layout)

The Ansible project has been split into reusable roles for easier debugging and maintenance:

```text
ansible-meerkat/
├── inventory.yml
├── group_vars/
│   └── all/
│       ├── network.yml
│       └── vault.yml
├── playbooks/
│   ├── router_garage.yml
│   ├── router_office_ap.yml
│   ├── router_office_ap_with_tailscale.yml
│   └── tasks/
│       ├── router_garage.yml
│       ├── router_office_ap_core.yml
│       └── router_office_ap_tailscale.yml
└── roles/
    ├── router_garage/
    │   ├── defaults/main.yml
    │   └── tasks/
    │       ├── main.yml
    │       ├── policy_and_validation.yml
    │       ├── core_network.yml
    │       ├── test_mode_checks.yml
    │       └── radio_policy.yml
    ├── router_office_ap/
    │   ├── defaults/main.yml
    │   └── tasks/main.yml
    ├── tailscale_openwrt/
    │   ├── defaults/main.yml
    │   └── tasks/main.yml
    ├── adguard_home_openwrt/
    │   ├── defaults/main.yml
    │   └── tasks/main.yml
    └── wireguard_policy_openwrt/
        ├── defaults/main.yml
        └── tasks/main.yml
```



## 0.1 Optional components added (AdGuard + WireGuard policy routing)

The garage playbook now includes two disabled-by-default components:

- **AdGuard Home** (`adguard_home_openwrt` role):
  - Installs AdGuard Home, renders baseline config, optionally disables DNS in `dnsmasq`,
    and pushes DHCP DNS options so VLAN clients use local router DNS.
  - Adds firewall rules to allow DNS (`53/tcp+udp`) from each VLAN zone and
    restricts AdGuard admin UI (`:3000`) to `trusted_zone` by default.

- **WireGuard policy routing** (`wireguard_policy_openwrt` role):
  - Installs WireGuard + `vpn-policy-routing` packages and defines multiple WG tunnels
    (example Surfshark London + Amsterdam).
  - Supports per-VLAN egress policies so e.g. IoT can use Amsterdam while other VLANs use London.

Both are controlled from `ansible-meerkat/group_vars/all/network.yml`:
- `services.adguard.enabled: false` (set true to apply),
- `services.wireguard_policy.enabled: false` (set true to apply after filling Vault secrets).

## 0. Factory-Reset to Ansible (GL.iNet + `community.openwrt`)

This section is the **direct path** from a factory-reset GL.iNet router to a working Ansible run using the official OpenWrt collection:

- Collection: <https://galaxy.ansible.com/ui/repo/published/community/openwrt/>
- Playbooks in this repo: `ansible-meerkat/playbooks/router_garage.yml`, `ansible-meerkat/playbooks/router_office_ap.yml`, and `ansible-meerkat/playbooks/router_office_ap_with_tailscale.yml`.

### 0.1 Preconditions

- You have a laptop/workstation with Python 3.10+.
- You can connect by Ethernet to each router during setup.
- You can factory reset both role hosts (`router-garage` and `router-office`).

### 0.2 Factory reset each GL.iNet device

Do this **one device at a time**:

1. Power on router.
2. Hold **RESET** for ~10 seconds until LEDs indicate reset/reboot.
3. Wait until router is fully booted.
4. Connect your computer to LAN.
5. Browse to `http://192.168.8.1` and set the admin password.
6. Enable SSH in GL.iNet admin if needed and verify:
   ```bash
   ssh root@192.168.8.1
   ```

> Both routers factory-reset to `192.168.8.1`, so configure Router Garage first, then disconnect it before doing Router Office.

### 0.3 Install Ansible and the OpenWrt collection

On your control machine:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install "ansible-core>=2.16"
ansible-galaxy collection install -r ansible-meerkat/requirements.yml
```

### 0.3.1 Use Ansible Vault for secrets

- Non-secrets are in `ansible-meerkat/group_vars/all/network.yml`.
- Secrets are in `ansible-meerkat/group_vars/all/vault.yml` (encrypt this file).
- Add WAN PPPoE secrets in Vault:
  - `vault_garage_wan_pppoe_username`
  - `vault_garage_wan_pppoe_password`
- Add optional test-mode repeater secrets in Vault:
  - `vault_garage_test_repeater_ssid`
  - `vault_garage_test_repeater_password`
- Add Tailscale OAuth secrets in Vault (if using OAuth instead of a static auth key):
  - `vault_tailscale_oauth_client_id`
  - `vault_tailscale_oauth_client_secret`
- Set garage WAN VLAN tag in `network.yml` (default in repo: `network.garage.wan.pppoe.vlan_tag: '911'`).

```bash
# safest way to update secrets (decrypts in editor, then re-encrypts on save)
ansible-vault edit ansible-meerkat/group_vars/all/vault.yml

# read without writing plaintext to disk
ansible-vault view ansible-meerkat/group_vars/all/vault.yml

# temporary full decrypt/re-encrypt workflow
ansible-vault decrypt ansible-meerkat/group_vars/all/vault.yml
ansible-vault encrypt ansible-meerkat/group_vars/all/vault.yml
```

OAuth notes:
- Preferred bootstrap: use OAuth client secret (`tskey-client-...`) as `tailscale_auth_key`, or store it in `vault_tailscale_oauth_client_secret` and let the playbook use it as `--auth-key` automatically.
- OAuth client must include permission to create auth keys.
- OAuth tags should allow `tag:router-garage` (configurable via `tailscale_oauth_tags`) and must be permitted by your tailnet ACL `tagOwners`.

Test mode notes:
- Set `network.garage.test_mode.enabled: true` in `ansible-meerkat/group_vars/all/network.yml`.
- In test mode, the router joins your upstream Wi-Fi as repeater uplink (`wwan`) and keeps Wi-Fi radios enabled so internet remains available for Tailscale.
- In test mode, PPPoE WAN configuration is skipped.
- In test mode, repeater config defaults to `network.garage.test_mode.repeater.radio: 'radio1'` and `network.garage.test_mode.repeater.encryption: 'sae'` (5 GHz + WPA3). The playbook also scans candidate radios and picks the first one that sees your configured repeater SSID.
- In test mode, uplink validation waits up to `network.garage.test_mode.uplink_wait_seconds` (default `90`) and polls every `network.garage.test_mode.uplink_poll_interval_seconds` (default `5`) before failing.
- In test mode, the playbook verifies repeater uplink internet (`8.8.8.8`/`1.1.1.1`) and control-plane reachability to `login.tailscale.com` + `api.tailscale.com`; if those fail, the run fails fast.
- In live/prod mode (`network.garage.test_mode.enabled: false`), radios can be disabled after WAN/internet checks pass.

```bash
ansible-vault encrypt ansible-meerkat/group_vars/all/vault.yml
```

Use one of these options when running playbooks after encrypting:

```bash
--ask-vault-pass
```

or

```bash
--vault-password-file ~/.ansible/.vault_pass.txt
```

SSH bootstrap note:
- `ansible-meerkat/inventory.yml` sets `ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'` for lab convenience, so factory resets do not require cleaning `~/.ssh/known_hosts`.

### 0.4 Configure Router Garage (gateway) from factory defaults

1. Connect only to Router Garage at `192.168.8.1`.
   > Inventory defaults to `router-garage=10.1.0.1` after bootstrap.  
   > For a factory-reset run, override host once:
   > ```bash
   > -e ansible_host=192.168.8.1
   > ```
2. Check SSH connectivity:
   ```bash
   ansible -i ansible-meerkat/inventory.yml gateway -m ping -k -e ansible_host=192.168.8.1
   ```
   > `ansible.builtin.ping` is a Python-based test module and expects a Python interpreter on the target.
   > OpenWrt/GL.iNet images often do not ship with Python, so use a raw SSH check instead when bootstrapping:
   > ```bash
   > ansible -i ansible-meerkat/inventory.yml gateway -m ansible.builtin.raw -a 'echo ok' -k -e ansible_host=192.168.8.1
   > ```
3. Run playbook:
   ```bash
   ansible-playbook -i ansible-meerkat/inventory.yml ansible-meerkat/playbooks/router_garage.yml -k --ask-vault-pass -e ansible_host=192.168.8.1
   ```
4. The playbook configures garage WAN as PPPoE on VLAN `911` (using vault credentials) when not in test mode, renames garage SSIDs to `homelab_garage_mngmt`, and runs the reusable Tailscale component configured for exit-node + route advertisements.
   - Live/prod mode: disables 2.4/5 GHz radios only after WAN + internet are confirmed up.
   - Test mode (`network.garage.test_mode.enabled: true`): configures Wi-Fi repeater uplink and keeps radios enabled.
5. Reconnect your workstation so it can reach the new router IP (`10.1.0.1`).

### 0.5 Configure Router Office (AP) from factory defaults

1. Disconnect Router Garage from your setup network (avoid IP conflict).
2. Factory reset Router Office and connect to it at `192.168.8.1`.
3. Check SSH connectivity:
   ```bash
   ansible -i ansible-meerkat/inventory.yml access_points -m ping -k
   ```
   > If Python is missing on the AP, prefer:
   > ```bash
   > ansible -i ansible-meerkat/inventory.yml access_points -m ansible.builtin.raw -a 'echo ok' -k
   > ```
4. Run core AP playbook:
   ```bash
   ansible-playbook -i ansible-meerkat/inventory.yml ansible-meerkat/playbooks/router_office_ap.yml -k --ask-vault-pass
   ```
   Optional: join Office AP to tailnet without advertising exit-node/routes:
   ```bash
   ansible-playbook -i ansible-meerkat/inventory.yml ansible-meerkat/playbooks/router_office_ap_with_tailscale.yml -k --ask-vault-pass
   ```
5. After playbook, office AP host should be reachable at `10.1.0.4`.

### 0.6 Recommended post-checks

```bash
ssh root@10.1.0.1 "uci show network.lan"
ssh root@10.1.0.4 "uci show network.lan"
ssh root@10.1.0.4 "uci show dhcp.lan"
```

If desired, replace `-k` with SSH keys once initial provisioning is complete.

---



## VPN architecture feasibility notes (per-VLAN Surfshark locations)

Yes, per-VLAN VPN egress is possible on OpenWrt with policy-based routing:

1. Bring up multiple WireGuard interfaces (one per location/provider endpoint).
2. Attach them to a dedicated firewall zone (e.g. `vpn`).
3. Use `vpn-policy-routing` policies to map source subnets to a specific WG interface.

Example mapping supported by the new vars in this repo:
- `10.30.0.0/24` (IoT VLAN) -> `wg_surfshark_amsterdam`
- `10.20.0.0/24`, `10.10.0.0/24`, `10.99.0.0/24` -> `wg_surfshark_london`

### Caveats
- Some OpenWrt builds use package name `pbr` instead of `vpn-policy-routing`.
- Multiple full-tunnel peers (`0.0.0.0/0`) can conflict if policy rules are incomplete.
- Throughput depends heavily on router CPU + WireGuard acceleration support.

### “API-like” location switching without router login

The easiest path is to make location changes in Ansible vars and run a component playbook:

```bash
ansible-playbook -i ansible-meerkat/inventory.yml ansible-meerkat/playbooks/router_garage.yml --tags wireguard --ask-vault-pass
```

If you want true one-click switching, you can expose a small CI job (GitHub Actions/Jenkins)
that updates `wireguard_policy_vlan_map` and runs the same playbook.

## 1. Network Topology

### **Zone A: Garage (Core & MDF)**
* **Role:** Internet Entry, Routing, Storage, Compute.
* **Hardware:**
    * **Router role host (`router-garage`):** GL.iNet/OpenWrt router (example: Flint 2).
    * **Switch:** 8x 2.5GbE + 2x 10GbE SFP+ (Unmanaged).
    * **Servers:** NAS (10GbE), Rack Desktop (10GbE), Zimaboard/Blade.
* **Connections:**
    * **ISP Fibre** -> Router Garage WAN (PPPoE/Static IP).
    * **Router Garage LAN** -> Core Switch Port 1 (2.5GbE).
    * **NAS** -> Core Switch SFP+ Port 1.
    * **Rack Desktop** -> Core Switch SFP+ Port 2.
    * **Uplink to Office** -> Core Switch 2.5GbE Port -> Wall Socket (Cable A).

### **Zone B: Office (Edge)**
* **Role:** User Access, WiFi Broadcast, Workstation Peripherals.
* **Hardware:**
    * **Switch:** 5x 2.5GbE PoE (Unmanaged).
    * **Office AP role host (`router-office`):** GL.iNet/OpenWrt router in AP mode (currently tested with Beryl MT3000).
    * **KVM:** Receiver Console.
* **Connections:**
    * **Wall Socket (Cable A)** -> Office Switch Uplink.
    * **Office Switch** -> Router Office WAN/LAN Port (2.5GbE).
    * **Wall Socket (Cable B)** -> KVM Receiver (Direct link to Garage).

---

## 2. IP & VLAN Schema
**Structure:** `10.VLAN.x.x` (Class A Private).

| VLAN ID | Name | Subnet | Gateway | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Mgmt** | `10.1.0.0/24` | `10.1.0.1` | Network Gear (Switches, APs, Router). |
| **10** | **Servers** | `10.10.0.0/24` | `10.10.0.1` | NAS, Proxmox, Docker, Pis. |
| **20** | **Trusted** | `10.20.0.0/24` | `10.20.0.1` | Desktop, Laptops, Phones. |
| **30** | **IoT** | `10.30.0.0/24` | `10.30.0.1` | Smart Home, Cameras, TV. |
| **99** | **Guest** | `10.99.0.0/24` | `10.99.0.1` | Visitors. |

### **Static IP Assignments**
* **`router-garage` (Router):** `10.1.0.1`
* **`router-office` (AP):** `10.1.0.4`
* **NAS:** `10.10.0.5`
* **Rack Desktop:** `10.20.0.5`
* **Reverse Proxy Server:** `10.10.0.20` (Hosting `meerkat.lan`)

---

## 3. Router Configuration (`router-garage` - Garage)

**Note:** Configuration performed via LuCI (`Advanced Settings`).

### **Interfaces**
1.  **LAN (br-lan):**
    * Enable **VLAN Filtering**.
    * Add VLANs: `10`, `20`, `30`, `99`.
    * **Port Settings:** Ensure the LAN port connecting to the switch is set to **Tagged (T)** for all VLANs.
2.  **VLAN Interfaces:**
    * Create `Interface_Servers` -> Protocol: Static -> IP: `10.10.0.1` -> Device: `br-lan.10`.
    * Create `Interface_Trusted` -> Protocol: Static -> IP: `10.20.0.1` -> Device: `br-lan.20`.
    * Create `Interface_IoT` -> Protocol: Static -> IP: `10.30.0.1` -> Device: `br-lan.30`.
    * *Enable DHCP Server for all.*
3.  **WAN:**
    * Protocol: **PPPoE**.
    * VLAN tag: **911** (`network.garage.wan.pppoe.vlan_tag`).
    * Credentials: sourced from Ansible Vault (`vault_garage_wan_pppoe_username` / `vault_garage_wan_pppoe_password`).

### **Firewall Zones**
| Zone Name | Input | Output | Forward | Masquerading | Allowed Forward To |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **lan** (Mgmt) | Accept | Accept | Accept | No | wan, server_zone |
| **server_zone** | Accept | Accept | Accept | No | wan |
| **trusted_zone** | Accept | Accept | Reject | No | wan, server_zone |
| **iot_zone** | Reject | Accept | Reject | No | wan |
| **guest_zone** | Reject | Accept | Reject | No | wan |

* **Rule:** `trusted_zone` -> `server_zone` (Allow Port 80/443/SSH).
* **Rule:** `iot_zone` -> `lan` (BLOCK - Default).

---

## 4. WiFi Configuration (`router-office` - Office)

**Mode:** Access Point (AP) / Extender.

### **SSID Settings**
| SSID | Band | VLAN ID | Security | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Meerkat Manor** | 5GHz / 6GHz | `20` | WPA3-SAE | High Speed (Laptops, Phones) |
| **Meerkat IoT** | 2.4GHz | `30` | WPA2-PSK | Smart Plugs, Cameras |
| **Meerkat Guest** | 2.4GHz / 5GHz | `99` | WPA2/3 | Visitors |

**Setup Note:** In LuCI on Router Office, bridge the SSID interfaces to the corresponding VLANs (e.g., `br-lan.20`).

---

## 5. Wired Device Configuration (Unmanaged Switch Workaround)

**Constraint:** The switches are unmanaged and cannot assign VLANs to ports.  
**Solution:** End devices must tag their own traffic.

### **Rack Desktop (Windows 11)**
1.  Device Manager -> Network Adapters -> 10GbE Card.
2.  Properties -> Advanced -> **VLAN ID**.
3.  Value: `20`.

### **NAS / Servers (Linux/Unraid)**
1.  Network Settings.
2.  Create VLAN Interface (e.g., `eth0.10`).
3.  Assign Static IP `10.10.0.5`.

---

## 6. Internal Services & DNS (`meerkat.lan`)

### **DNS: AdGuard Home (On Router Garage)**
* **Location:** Applications -> AdGuard Home -> Settings.
* **DNS Rewrites:**
    * Domain: `*.meerkat.lan`
    * Answer: `10.10.0.20` (Server IP).

### **Reverse Proxy: Nginx Proxy Manager**
* **Host:** Docker Container on `10.10.0.20`.
* **Proxy Hosts:**
    * `plex.meerkat.lan` -> `10.10.0.5:32400`
    * `nas.meerkat.lan` -> `10.10.0.5:5000`
    * `router.meerkat.lan` -> `10.1.0.1:80`
    * `ha.meerkat.lan` -> `10.30.0.50:8123` (Home Assistant)

### **VPN: Tailscale**
* **Role split:** `tailscale_openwrt` is reusable for any OpenWrt device, and the playbook components decide whether a node advertises exit-node/routes.
* **Garage profile:** advertises exit-node + `10.10.0.0/24` and `10.20.0.0/24`.
* **Office AP profile:** joins tailnet without advertising exit-node/routes (via `router_office_ap_with_tailscale.yml`).
* **Auth:** If the node is not already authenticated, set `tailscale_auth_key` in Vault (standard auth key or OAuth client secret `tskey-client-...`) or run `tailscale up` manually once on the router.
