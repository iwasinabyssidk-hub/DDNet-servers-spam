# DDNet-servers-spam

Python script to flood the DDNet master server with fake servers and fake players.  
Useful for stress testing, filling the server list, or just trolling.

---

## 🚀 Features

- Spawns **N fake servers** on a single VPS (configurable)
- Each server reports **fake players** with custom names and stats
- Responds to **info requests** (both `inf3` and legacy `dtsf`)
- Handles **extended info** (`iext`) for modern DDNet clients
- Automatically **registers** with the DDNet master server
- Supports **challenge-response** handshake (master server validation)
- Simulates **connection attempts** (optional reject message)
- UDP listeners run in separate threads for each server

---

## 🛠️ Configuration

Edit the variables at the top of the script:

| Variable | Description |
|----------|-------------|
| `BASE_PORT` | Starting UDP port (default: 8303) |
| `NUM_SERVERS` | Number of fake servers to create |
| `SERVER_IP` | Your VPS public IP (must match master server expectations) |
| `MASTER_URL` | DDNet master server endpoint |
| `SERVER_NAME` | Name displayed in the server list |
| `MAP_NAME` | Map name shown in the server list |
| `GAMETYPE` | Game type (e.g., "CHEAT", "DM", "CTF") |
| `VERSION` | Protocol version (should match DDNet client) |
| `FAKE_PLAYERS` | Number of fake players per server |
| `FAKE_MAX_CLIENTS` | Max players shown in the server list |
| `REJECT_MESSAGE` | Optional message sent when a client tries to connect |

---

## 📦 Requirements

- Python 3.6+
- Standard library only (`socket`, `threading`, `urllib`, `json`, `uuid`)

No external dependencies needed.

---

## 🧪 Usage

### ⚠️ Important: Network Requirements

The script **must** be run on a machine with:
- **Public (white) IP address** — the master server needs to reach your server via UDP
- **Open UDP ports** in the range `BASE_PORT` to `BASE_PORT + NUM_SERVERS - 1`
- **No NAT or firewall blocking** incoming UDP traffic on those ports

**Recommended**: Run on a **VPS (Virtual Private Server)** with a public IP.  
Running on a home computer behind a router (NAT) will **not work** unless you configure port forwarding and the router has a public IP.

### Running the Script

1. **Edit the configuration** section with your VPS IP and desired parameters.
2. Run the script:

```bash
python3 ddnet_spam.py
Wait for the script to start all servers. You'll see output like:

text
🚀 Запускаю 1000 фейковых серверов BEST EXTERNAL
📡 Порты: 8303 - 9802
🌐 IP: 155.212.147.186
🔗 Дискорд: dsc.gg/dreamingddnet
==================================================
[MASTER][8303] Registered
[MASTER][8304] Registered
...
✅ 1000 servers are on
❌ Ctrl+C to stop
Press Ctrl+C to stop all servers.

⚙️ How It Works
UDP Server Thread (per port)
Listens for incoming UDP packets from clients or master servers.

Handles:

gie3 / fstd → returns fake server info (ddrace_server_info_payload)

iext → returns extended info (ddrace_extended_info_payload)

chal → stores challenge token for master server handshake

0x0b → connection attempt → sends reject message (optional)

Master Registration Thread (per server)
Every 15 seconds, sends a JSON payload to the DDNet master server.

Payload includes:

Server metadata (name, map, gametype, version)

List of fake players (names, clans, scores)

Handles master server responses:

success → registration OK

need_challenge → triggers challenge-response flow

need_info → increments Info-Serial counter

Fake Player Data
Names: dumbass001, dumbass002, ...

Clan: BEST

Score: 1337

Country: -1 (unknown)

Number of fake players is limited by the DDNet protocol:

Basic info: up to 333 players

Extended info: up to 45 players

⚠️ Disclaimer
This script is intended for educational and testing purposes only.
Spamming the official DDNet master server may violate their terms of service and could result in a permanent ban of your IP.

Use at your own risk. The author is not responsible for any consequences.
