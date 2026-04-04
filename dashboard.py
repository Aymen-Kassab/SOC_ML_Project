import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import os
from datetime import datetime, timedelta

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SOC // Terminal X",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── GLOBAL CSS (STABILIZED) ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;700&family=Orbitron:wght@400;900&display=swap');

/* Base UI */
html, body, [data-testid="stAppViewContainer"] {
    background: #050a0f !important;
    color: #c8d8e8 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* The Cyber Grid Background */
[data-testid="stAppViewContainer"] {
    background: 
        linear-gradient(rgba(0, 180, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 180, 255, 0.03) 1px, transparent 1px),
        #050a0f !important;
    background-size: 30px 30px !important;
}

/* Professional Metrics */
.metric-card {
    background: #0a1520;
    border: 1px solid rgba(0,180,255,0.2);
    border-top: 3px solid #00b4ff;
    border-radius: 4px;
    padding: 15px;
    text-align: left;
}
.danger { border-top-color: #ff2244 !important; }
.warning { border-top-color: #ffaa00 !important; }

.m-label { font-family: 'Share Tech Mono'; font-size: 10px; color: #3a6a8a; letter-spacing: 2px; }
.m-value { font-family: 'Orbitron'; font-size: 24px; color: #fff; text-shadow: 0 0 10px rgba(0,180,255,0.5); }

/* Status Pulse */
.status-live { color: #00ff88; font-family: 'Share Tech Mono'; font-size: 12px; }
.pulse {
    height: 10px; width: 10px; background-color: #00ff88; border-radius: 50%;
    display: inline-block; box-shadow: 0 0 8px #00ff88; animation: blink 1s infinite;
}
@keyframes blink { 50% { opacity: 0.3; } }

/* Alerts */
.alert-row {
    font-family: 'Share Tech Mono'; font-size: 12px;
    padding: 8px; border-bottom: 1px solid rgba(0,180,255,0.1);
    display: flex; justify-content: space-between;
}
</style>
""", unsafe_allow_html=True)

# ─── DATA ENGINE ─────────────────────────────────────────────────────────────
LOG_FILE = "ids_detection_logs.csv" # Adjusted for root folder access

def load_data():
    if os.path.exists(LOG_FILE):
        try:
            df = pd.read_csv(LOG_FILE)
            df.columns = [c.strip() for c in df.columns]
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            return df.sort_values("Timestamp", ascending=False)
        except:
            return _generate_mock()
    return _generate_mock()

def _generate_mock():
    # Fallback to keep the UI beautiful even if logs are empty
    now = datetime.now()
    data = []
    for i in range(20):
        data.append({
            "Timestamp": now - timedelta(seconds=i*10),
            "Source_IP": f"192.168.1.{10+i}",
            "Packets": np.random.randint(10, 5000),
            "Status": np.random.choice(["BENIGN", "PortScan", "DoS", "SSH-Patator"]),
            "Method": np.random.choice(["AI", "Heuristic"])
        })
    return pd.DataFrame(data)

# ─── HEADER ──────────────────────────────────────────────────────────────────
c1, c2 = st.columns([4, 1])
with c1:
    st.markdown('<h1 style="color:#00b4ff; font-family:Orbitron; letter-spacing:5px;">SENTINEL X-RAY</h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Share Tech Mono; color:#3a6a8a;">SEC-OPS TERMINAL // LEVEL 4 CLEARANCE</p>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div style="text-align:right"><span class="pulse"></span> <span class="status-live">LIVE FEED</span><br><code style="color:#3a6a8a">{datetime.now().strftime("%H:%M:%S")}</code></div>', unsafe_allow_html=True)

# ─── LOGIC & REFRESH ─────────────────────────────────────────────────────────
df = load_data()
df_threats = df[df['Status'] != 'BENIGN']

# ─── TOP METRICS ─────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f'''<div class="metric-card">
        <div class="m-label">TOTAL SESSIONS</div><div class="m-value">{len(df)}</div>
    </div>''', unsafe_allow_html=True)
with m2:
    st.markdown(f'''<div class="metric-card danger">
        <div class="m-label">ACTIVE ALERTS</div><div class="m-value">{len(df_threats)}</div>
    </div>''', unsafe_allow_html=True)
with m3:
    st.markdown(f'''<div class="metric-card warning">
        <div class="m-label">THREAT SOURCES</div><div class="m-value">{df_threats["Source_IP"].nunique()}</div>
    </div>''', unsafe_allow_html=True)
with m4:
    load = df.tail(10)['Packets'].sum()
    st.markdown(f'''<div class="metric-card">
        <div class="m-label">NETWORK LOAD (INST)</div><div class="m-value">{load} pkts</div>
    </div>''', unsafe_allow_html=True)

st.write("") # Spacer

# ─── CHARTS ──────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown('<p style="font-family:Share Tech Mono; font-size:12px; color:#3a6a8a;">// TRAFFIC PULSE (50 EVENTS)</p>', unsafe_allow_html=True)
    # Using a professional Area Chart for spikes
    fig = px.area(df.head(50), x="Timestamp", y="Packets", color_discrete_sequence=['#00b4ff'])
    fig.update_layout(height=250, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_right:
    st.markdown('<p style="font-family:Share Tech Mono; font-size:12px; color:#3a6a8a;">// ATTACK VECTORS</p>', unsafe_allow_html=True)
    if not df_threats.empty:
        fig_pie = px.pie(df_threats, names='Status', hole=0.6, color_discrete_sequence=px.colors.sequential.Blues_r)
        fig_pie.update_layout(height=250, template="plotly_dark", showlegend=False, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("NO THREATS")

# ─── LIVE FEED ───────────────────────────────────────────────────────────────
st.markdown('<p style="font-family:Share Tech Mono; font-size:12px; color:#3a6a8a; border-bottom:1px solid #1e293b;">// RAW TELEMETRY FEED</p>', unsafe_allow_html=True)

# High-speed data table with custom coloring
def color_status(val):
    if val != "BENIGN": return 'color: #ff2244; font-weight: bold;'
    return 'color: #00ff88;'

st.dataframe(
    df.head(15).style.applymap(color_status, subset=['Status']),
    use_container_width=True,
    hide_index=True
)

# ─── THE 2-SECOND REFRESH ────────────────────────────────────────────────────
time.sleep(2)
st.rerun()