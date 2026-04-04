import numpy as np
import joblib
from scapy.all import sniff, IP, TCP, ARP
import time
import csv
import os
import warnings

warnings.filterwarnings("ignore")

# Configuration
INTERFACE = "enp0s3"
MODEL_PATH = "multiclass_ids_model.pkl"
SCALER_PATH = "multiclass_ids_scaler.pkl"
WINDOW_DURATION = 5
LOG_FILE = "..\Logs\ids_detection_logs.csv"

ip_mac_table = {}
label_map = {0: "BENIGN", 1: "PortScan", 2: "DoS", 3: "SSH-Patator"}

# Load model and scaler
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)


def log_event(ip, packets, status, method):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Source_IP", "Packets", "Status", "Detection_Method"])
        writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), ip, packets, status, method])


def fast_arp_check(p):
    if p.haslayer(ARP) and p[ARP].op == 2:  # ARP Response
        spa, sha = p[ARP].psrc, p[ARP].hwsrc
        if spa in ip_mac_table and ip_mac_table[spa] != sha:
            print(f"\n\033[41m[ALERT] ARP SPOOFING DETECTED: {spa} is at {sha}\033[0m\n")
            log_event(spa, "N/A", "ARP_SPOOFING", "MAC_RULE")
        ip_mac_table[spa] = sha


def analyze_window(pkts):
    if not pkts:
        return

    stats = {}

    for p in pkts:
        if p.haslayer(IP):
            src = p[IP].src

            # Filter management/local traffic
            if src == "127.0.0.1" or src == "192.168.56.1":
                continue

            if src not in stats:
                stats[src] = {
                    'ports': [],
                    'start': p.time,
                    'end': p.time,
                    'pkts': 0,
                    'bytes': 0,
                    'syn': 0,
                    'ack': 0,
                    'rst': 0
                }

            s = stats[src]
            s['pkts'] += 1
            s['bytes'] += len(p)
            s['end'] = p.time

            if p.haslayer(TCP):
                if p[TCP].dport not in s['ports']:
                    s['ports'].append(p[TCP].dport)
                flags = p[TCP].flags
                if 'S' in flags: s['syn'] += 1
                if 'A' in flags: s['ack'] += 1
                if 'R' in flags: s['rst'] += 1

    for ip, d in stats.items():
        # Feature Engineering
        duration = max((d['end'] - d['start']) * 1e6, 1)
        avg_pkt_size = d['bytes'] / d['pkts'] if d['pkts'] else 0
        dest_port = min(d['ports']) if d['ports'] else 0
        fwd_pkts = d['pkts']
        bwd_pkts = int(d['pkts'] * 0.3)

        features = [
            dest_port, duration, fwd_pkts, bwd_pkts, avg_pkt_size,
            d['syn'], d['ack'], d['rst'],
            (d['bytes'] / duration) * 1e6, (d['pkts'] / duration) * 1e6
        ]

        # ML Prediction
        X = scaler.transform([features])
        probs = model.predict_proba(X)[0]

        # Hybrid Decision Logic
        u_ports = len(set(d['ports']))
        method = "AI"

        if u_ports > 10:
            status = "PortScan"
            method = "Heuristic"
        elif d['pkts'] > 1000:
            status = "DoS"
            method = "Heuristic"
        elif probs[3] > 0.2:
            status = "SSH-Patator"
        elif probs[2] > 0.2:
            status = "DoS"
        else:
            status = "BENIGN"

        # --- KEY FIX: Log everything to the CSV here ---
        log_event(ip, d['pkts'], status, method)

        # UI Feedback
        if status == "BENIGN":
            print(f"[OK] {ip} Normal")
        else:
            print(f"\033[91m[ALERT] {ip} -> {status} ({method})\033[0m")


print(f"IDS running on {INTERFACE}... (Management Traffic Filtered)")

while True:
    try:
        sniffed = sniff(iface=INTERFACE, timeout=WINDOW_DURATION, prn=fast_arp_check)
        analyze_window(sniffed)
    except KeyboardInterrupt:
        print("\nStopping IDS...")
        break