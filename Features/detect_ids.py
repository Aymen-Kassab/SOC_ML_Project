import pandas as pd
import numpy as np
import joblib
from scapy.all import sniff, IP, TCP, ARP, Ether
import time
import warnings
import csv  # Added for logging
import os  # Added for logging

warnings.filterwarnings("ignore")

# ==================================================
# CONFIGURATION
# ==================================================
INTERFACE = "VirtualBox Host-Only Ethernet Adapter"
MODEL_PATH = "../Models/multiclass_ids_model.pkl"
SCALER_PATH = "../Models/multiclass_ids_scaler.pkl"
WINDOW_DURATION = 3
LOG_FILE = "../Logs/ids_detection_logs.csv"

# Key: IP Address -> Value: Real MAC Address
ip_mac_table = {}

print("Loading AI Models...")
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    label_map = {0: "BENIGN", 1: "PortScan", 2: "DoS", 3: "SSH-Patator"}
    print("Models Loaded.")
except Exception as e:
    print(f"Error: {e}")
    exit()


# --- NEW: LOGGING FUNCTION ---
def log_detection(ip, packets, status):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        # Write the header only if the file is being created for the first time
        if not file_exists:
            writer.writerow(["Timestamp", "Source_IP", "Packet_Count", "Detection_Status"])

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([timestamp, ip, packets, status])


def analyze_window(pkts):
    if not pkts:
        return

    ip_stats = {}

    for p in pkts:
        # --- 1) LAYER 2: ARP SPOOFING LOGIC ---
        if p.haslayer(ARP):
            if p[ARP].op == 2:
                src_ip = p[ARP].psrc
                src_mac = p[ARP].hwsrc

                if src_ip in ip_mac_table and ip_mac_table[src_ip] != src_mac:
                    alert_msg = "ARP SPOOFING DETECTED"
                    print(f"\n[!] {alert_msg}!")
                    print(f"    CONFLICT: {src_ip} is claimed by {src_mac}")
                    log_detection(src_ip, "N/A", alert_msg)  # Log ARP Alert
                else:
                    ip_mac_table[src_ip] = src_mac

        # --- 2) LAYER 4: AI DETECTION LOGIC ---
        if p.haslayer(IP):
            src = p[IP].src
            if src == "127.0.0.1": continue

            if src not in ip_stats:
                ip_stats[src] = {
                    'ports': set(), 'start': p.time, 'end': p.time,
                    'pkts': 0, 'bytes': 0, 'syn': 0, 'ack': 0, 'rst': 0
                }

            s = ip_stats[src]
            s['pkts'] += 1
            s['bytes'] += len(p)
            s['end'] = p.time

            if p.haslayer(TCP):
                s['ports'].add(p[TCP].dport)
                flags = p[TCP].flags
                if 'S' in flags: s['syn'] += 1
                if 'A' in flags: s['ack'] += 1
                if 'R' in flags: s['rst'] += 1

    if ip_stats:
        print(f"\n--- [ Analysis @ {time.strftime('%H:%M:%S')} ] ---")
        for ip, data in ip_stats.items():
            duration = float((data['end'] - data['start']) * 1e6) or 1.0

            features = [
                list(data['ports'])[0] if data['ports'] else 0,
                duration, data['pkts'], 0, data['bytes'] / data['pkts'],
                data['syn'], data['ack'], data['rst'],
                                           (data['bytes'] / duration) * 1e6, (data['pkts'] / duration) * 1e6
            ]

            X = scaler.transform([features])
            pred = model.predict(X)[0]
            status = label_map[pred]

            # Heuristics for demo stability
            u_ports = len(data['ports'])
            if u_ports > 15:
                status = "PortScan"
            elif data['pkts'] > 100 and u_ports < 5:
                status = "DoS"
            elif data['pkts'] > 15 and 22 in data['ports']:
                status = "SSH-Patator"

            print(f"IP: {ip:<15} | Packets: {data['pkts']:<5} | Status: {status}")

            # --- LOG THE DETECTION TO CSV ---
            log_detection(ip, data['pkts'], status)


print(f"HYBRID IDS STARTING ON {INTERFACE}...")
while True:
    try:
        sniffed_packets = sniff(iface=INTERFACE, timeout=WINDOW_DURATION)
        analyze_window(sniffed_packets)
    except KeyboardInterrupt:
        print("\nStopping IDS...")
        break