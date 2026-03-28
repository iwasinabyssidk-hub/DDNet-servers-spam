import socket
import threading
import time
import json
import urllib.request
import urllib.error
import uuid

#config

BASE_PORT = 8303 #dont change
NUM_SERVERS = 1000  #how many servers will be in list
SERVER_IP = "155.212.147.186"  #your vps ip

MASTER_URL = "https://master1.ddnet.org/ddnet/15/register"

SERVER_NAME = "BEST EXTERNAL - dsc.gg/dreamingddnet [64]" 
MAP_NAME = "dsc.gg/dreamingddnet"
GAMETYPE = "CHEAT"
VERSION = "16.4.0"
FAKE_PLAYERS = 666 #max
FAKE_MAX_CLIENTS = 666 #you can set there any number u want

REJECT_MESSAGE = ""

#protocol

def pack_str(s):
    return s.encode('utf-8') + b'\x00'

def pack_int_str(i):
    return pack_str(str(i))

def unpack_connless_packet(data):
    if len(data) >= 6 and data[:2] == b'xe':
        return True, data[2:6], data[6:]
    if len(data) >= 6 and data[:6] == b'\xff\xff\xff\xff\xff\xff':
        return False, b'\x00\x00\x00\x00', data[6:]
    return False, b'\x00\x00\x00\x00', data

def pack_connless_packet(payload, extended=False, extra=b'\x00\x00\x00\x00'):
    if extended:
        return b'xe' + (extra[:4] if extra else b'\x00\x00\x00\x00') + payload
    return b'\xff\xff\xff\xff\xff\xff' + payload

def ddrace_server_info_payload(port, token, type_legacy=False):
    resp = bytearray()
    if type_legacy:
        resp.extend(b'\xff\xff\xff\xffdtsf')
    else:
        resp.extend(b'\xff\xff\xff\xffinf3')

    resp.extend(pack_int_str(token))
    resp.extend(pack_str(VERSION))
    resp.extend(pack_str(SERVER_NAME))
    resp.extend(pack_str(MAP_NAME))
    resp.extend(pack_str(GAMETYPE))
    resp.extend(pack_int_str(0))
    resp.extend(pack_int_str(FAKE_PLAYERS))
    resp.extend(pack_int_str(FAKE_MAX_CLIENTS))
    resp.extend(pack_int_str(FAKE_PLAYERS))
    resp.extend(pack_int_str(FAKE_MAX_CLIENTS))

    for i in range(min(FAKE_PLAYERS, 333)):
        resp.extend(pack_str(f"dumbass{i+1:03d}"))
        resp.extend(pack_str("BEST"))
        resp.extend(pack_int_str(-1))
        resp.extend(pack_int_str(1337))
        resp.extend(pack_int_str(1))

    return resp

def ddrace_extended_info_payload(port, token):
    resp = bytearray()
    resp.extend(b'\xff\xff\xff\xffiext')
    resp.extend(pack_int_str(token))
    resp.extend(pack_str(VERSION))
    resp.extend(pack_str(SERVER_NAME))
    resp.extend(pack_str(MAP_NAME))
    resp.extend(pack_int_str(0))
    resp.extend(pack_int_str(0))
    resp.extend(pack_str(GAMETYPE))
    resp.extend(pack_int_str(0))
    resp.extend(pack_int_str(FAKE_PLAYERS))
    resp.extend(pack_int_str(FAKE_MAX_CLIENTS))
    resp.extend(pack_int_str(FAKE_PLAYERS))
    resp.extend(pack_int_str(FAKE_MAX_CLIENTS))
    resp.extend(pack_str(""))

    for i in range(min(FAKE_PLAYERS, 45)):
        resp.extend(pack_str(f"Bot {i}"))
        resp.extend(pack_str("BEST"))
        resp.extend(pack_int_str(-1))
        resp.extend(pack_int_str(1337))
        resp.extend(pack_int_str(1))
        resp.extend(pack_str(""))

    return resp

#udp server

def udp_server_thread(port, state):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(("0.0.0.0", port))
    except:
        print(f"[UDP][{port}] FAILED TO BIND - port in use")
        return
        
    sock.settimeout(1.0)
    print(f"[UDP][{port}] Listening")

    while True:
        try:
            data, addr = sock.recvfrom(4096)
            extended, extra, payload = unpack_connless_packet(data)

            if payload.startswith(b'\xff\xff\xff\xffgie3') and len(payload) >= 9:
                basic_token = payload[8]
                extra_token = (extra[0] << 8) | extra[1] if extended else 0
                token = basic_token | (extra_token << 8)
                resp_payload = ddrace_server_info_payload(port, token)
                sock.sendto(pack_connless_packet(resp_payload), addr)

            elif payload.startswith(b'\xff\xff\xff\xfffstd') and len(payload) >= 9:
                basic_token = payload[8]
                extra_token = (extra[0] << 8) | extra[1] if extended else 0
                token = basic_token | (extra_token << 8)
                resp_payload = ddrace_server_info_payload(port, token, type_legacy=True)
                sock.sendto(pack_connless_packet(resp_payload), addr)

            elif (payload.startswith(b'\xff\xff\xff\xffiext') or payload.startswith(b'\xff\xff\xff\xffiex+')) and len(payload) >= 9:
                basic_token = payload[8]
                extra_token = (extra[0] << 8) | extra[1] if extended else 0
                token = basic_token | (extra_token << 8)
                resp_payload = ddrace_extended_info_payload(port, token)
                sock.sendto(pack_connless_packet(resp_payload), addr)

            elif payload.startswith(b'\xff\xff\xff\xff\x0b'):
                error_msg = REJECT_MESSAGE.encode()
                response = b'\xff\xff\xff\xff\x0e' + error_msg
                sock.sendto(response, addr)
                print(f"[UDP][{port}] Connection attempt from {addr[0]}")

            elif payload.startswith(b'\xff\xff\xff\xffchal'):
                if len(payload) > 45:
                    remainder = payload[45:].split(b'\0')
                    if len(remainder) >= 2:
                        proto = remainder[0].decode('utf-8', errors='ignore')
                        token = remainder[1].decode('utf-8', errors='ignore')
                        state['challenge_token'] = token

        except socket.timeout:
            pass
        except Exception as e:
            pass

#registration

def master_registration_thread(port, state):
    info_serial = 1
    secret = str(uuid.uuid4())
    challenge_secret = str(uuid.uuid4())
    proto = "tw0.6/ipv4"
    addr_proto = "tw-0.6+udp://"

    while True:
        payload = {
            "max_clients": FAKE_MAX_CLIENTS,
            "max_players": FAKE_MAX_CLIENTS,
            "passworded": False,
            "game_type": GAMETYPE,
            "name": SERVER_NAME,
            "map": {
                "name": MAP_NAME,
                "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
                "size": 10000
            },
            "version": VERSION,
            "client_score_kind": "time",
            "requires_login": False,
            "clients": [{"name": f"dumbass{i+1:03d}", "clan": "BEST", "country": -1, "score": 1337, "is_player": True} for i in range(min(FAKE_PLAYERS, 333))]
        }

        req_headers = {
            'Content-Type': 'application/json',
            'Address': f'{addr_proto}connecting-address.invalid:{port}',  # ← исправлено
            'Secret': secret,
            'Challenge-Secret': f'{challenge_secret}:{proto}',
            'Info-Serial': str(info_serial),
            'User-Agent': f'Teeworlds DDNet {VERSION}'
        }

        if 'challenge_token' in state:
            req_headers['Challenge-Token'] = state['challenge_token']

        req = urllib.request.Request(MASTER_URL, data=json.dumps(payload).encode('utf-8'), headers=req_headers)

        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                resp_str = response.read().decode('utf-8')
                resp_json = json.loads(resp_str) if resp_str else {}
                status = resp_json.get("status", "success")
                if status == "success":
                    print(f"[MASTER][{port}] Registered")
                elif status == "need_challenge":
                    print(f"[MASTER][{port}] Need challenge")
                elif status == "need_info":
                    info_serial += 1
                    print(f"[MASTER][{port}] Info serial now {info_serial}")
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode('utf-8')
                print(f"[MASTER][{port}] HTTP {e.code}: {err_body[:100]}")
            except:
                print(f"[MASTER][{port}] HTTP {e.code}")
        except Exception as e:
            print(f"[MASTER][{port}] Failed: {e}")

        time.sleep(15)

#starting

def start_server(port):
    state = {}
    t_udp = threading.Thread(target=udp_server_thread, args=(port, state), daemon=True)
    t_master = threading.Thread(target=master_registration_thread, args=(port, state), daemon=True)
    t_udp.start()
    time.sleep(0.1)
    t_master.start()
    return (t_udp, t_master)

if __name__ == "__main__":
    print(f"🚀 Запускаю {NUM_SERVERS} фейковых серверов BEST EXTERNAL")
    print(f"📡 Порты: {BASE_PORT} - {BASE_PORT + NUM_SERVERS - 1}")
    print(f"🌐 IP: {SERVER_IP}")
    print(f"🔗 Дискорд: dsc.gg/dreamingddnet")
    print("=" * 50)

    threads = []
    success = 0
    for i in range(NUM_SERVERS):
        port = BASE_PORT + i
        try:
            threads.append(start_server(port))
            success += 1
            time.sleep(0.2)
        except:
            print(f"[!] Failed to start on port {port}")

    print(f"\n✅ {success} servers are on")
    print("❌ Ctrl+C to stop\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 stopping...")