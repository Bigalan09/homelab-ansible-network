# Homelab Network Documentation: Meerkat Manor

**Last Updated:** 2026-02-11  
**Location:** UK  
**Gateway Role Host:** `router-garage` (GL.iNet/OpenWrt device in Garage)  
**Office AP Role Host:** `router-office` (GL.iNet/OpenWrt device in Office, currently tested with Beryl MT3000)

---

## 0. Factory-Reset to Ansible (GL.iNet + `community.openwrt`)

This section is the **direct path** from a factory-reset GL.iNet router to a working Ansible run using the official OpenWrt collection:

- Collection: <https://galaxy.ansible.com/ui/repo/published/community/openwrt/>
- Playbooks in this repo: `ansible-meerkat/setup_router_garage.yml` and `ansible-meerkat/setup_router_office_ap.yml`

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

### 0.4 Configure Router Garage (gateway) from factory defaults

1. Connect only to Router Garage at `192.168.8.1`.
2. Check SSH connectivity:
   ```bash
   ansible -i ansible-meerkat/inventory.ini gateway -m ping -k
   ```
   > `ansible.builtin.ping` is a Python-based test module and expects a Python interpreter on the target.
   > OpenWrt/GL.iNet images often do not ship with Python, so use a raw SSH check instead when bootstrapping:
   > ```bash
   > ansible -i ansible-meerkat/inventory.ini gateway -m ansible.builtin.raw -a 'echo ok' -k
   > ```
3. Run playbook:
   ```bash
   ansible-playbook -i ansible-meerkat/inventory.ini ansible-meerkat/setup_router_garage.yml -k --ask-vault-pass
   ```
4. Reconnect your workstation so it can reach the new router IP (`10.1.0.1`).

### 0.5 Configure Router Office (AP) from factory defaults

1. Disconnect Router Garage from your setup network (avoid IP conflict).
2. Factory reset Router Office and connect to it at `192.168.8.1`.
3. Check SSH connectivity:
   ```bash
   ansible -i ansible-meerkat/inventory.ini access_points -m ping -k
   ```
   > If Python is missing on the AP, prefer:
   > ```bash
   > ansible -i ansible-meerkat/inventory.ini access_points -m ansible.builtin.raw -a 'echo ok' -k
   > ```
4. Run playbook:
   ```bash
   ansible-playbook -i ansible-meerkat/inventory.ini ansible-meerkat/setup_router_office_ap.yml -k --ask-vault-pass
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
* **Exit Node:** Enabled on Router Garage.
* **Subnet Routes:** Advertise `10.10.0.0/24` and `10.20.0.0/24`.
