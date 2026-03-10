import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import os
from datetime import datetime, timedelta
import random

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="SOC-ML | IDS Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# CUSTOM CSS - Dark Cybersecurity Theme
# ==================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

    /* Root theme */
    :root {
        --bg-primary: #050a0f;
        --bg-secondary: #0a1628;
        --bg-card: #0d1f35;
        --accent-green: #00ff88;
        --accent-cyan: #00d4ff;
        --accent-red: #ff3366;
        --accent-orange: #ff8c00;
        --accent-yellow: #ffd700;
        --text-primary: #e0f0ff;
        --text-muted: #5a7a99;
        --border: #1a3a5c;
    }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}

    /* Main background */
    .stApp {
        background: var(--bg-primary);
        background-image:
            radial-gradient(ellipse at 20% 50%, rgba(0, 212, 255, 0.03) 0%, transparent 60%),
            radial-gradient(ellipse at 80% 20%, rgba(0, 255, 136, 0.03) 0%, transparent 60%);
        font-family: 'Exo 2', sans-serif;
        color: var(--text-primary);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }

    /* Header banner */
    .ids-header {
        background: linear-gradient(135deg, #0a1628 0%, #0d2040 50%, #0a1628 100%);
        border: 1px solid var(--border);
        border-left: 4px solid var(--accent-cyan);
        border-radius: 8px;
        padding: 20px 30px;
        margin-bottom: 25px;
        position: relative;
        overflow: hidden;
    }
    .ids-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: repeating-linear-gradient(
            90deg,
            transparent,
            transparent 50px,
            rgba(0, 212, 255, 0.02) 50px,
            rgba(0, 212, 255, 0.02) 51px
        );
    }
    .ids-header h1 {
        font-family: 'Share Tech Mono', monospace;
        color: var(--accent-cyan);
        font-size: 1.8rem;
        margin: 0;
        letter-spacing: 3px;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
    }
    .ids-header p {
        color: var(--text-muted);
        font-size: 0.85rem;
        margin: 5px 0 0 0;
        font-family: 'Share Tech Mono', monospace;
        letter-spacing: 1px;
    }
    .status-live {
        display: inline-block;
        background: rgba(0, 255, 136, 0.1);
        border: 1px solid var(--accent-green);
        color: var(--accent-green);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-family: 'Share Tech Mono', monospace;
        letter-spacing: 2px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Metric cards */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: border-color 0.3s;
    }
    .metric-card:hover { border-color: var(--accent-cyan); }
    .metric-card::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 2px;
    }
    .metric-card.green::after { background: var(--accent-green); }
    .metric-card.red::after { background: var(--accent-red); }
    .metric-card.cyan::after { background: var(--accent-cyan); }
    .metric-card.orange::after { background: var(--accent-orange); }

    .metric-value {
        font-family: 'Share Tech Mono', monospace;
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 5px;
    }
    .metric-label {
        font-size: 0.75rem;
        color: var(--text-muted);
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .metric-card.green .metric-value { color: var(--accent-green); }
    .metric-card.red .metric-value { color: var(--accent-red); }
    .metric-card.cyan .metric-value { color: var(--accent-cyan); }
    .metric-card.orange .metric-value { color: var(--accent-orange); }

    /* Section headers */
    .section-header {
        font-family: 'Share Tech Mono', monospace;
        color: var(--accent-cyan);
        font-size: 0.85rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        border-bottom: 1px solid var(--border);
        padding-bottom: 8px;
        margin-bottom: 15px;
    }

    /* Alert badges in table */
    .badge-benign {
        background: rgba(0,255,136,0.15);
        color: #00ff88;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        border: 1px solid rgba(0,255,136,0.3);
        font-family: 'Share Tech Mono', monospace;
    }
    .badge-portscan {
        background: rgba(255,140,0,0.15);
        color: #ff8c00;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        border: 1px solid rgba(255,140,0,0.3);
        font-family: 'Share Tech Mono', monospace;
    }
    .badge-dos {
        background: rgba(255,51,102,0.15);
        color: #ff3366;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        border: 1px solid rgba(255,51,102,0.3);
        font-family: 'Share Tech Mono', monospace;
    }
    .badge-ssh {
        background: rgba(255,215,0,0.15);
        color: #ffd700;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        border: 1px solid rgba(255,215,0,0.3);
        font-family: 'Share Tech Mono', monospace;
    }
    .badge-arp {
        background: rgba(180,0,255,0.15);
        color: #cc44ff;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        border: 1px solid rgba(180,0,255,0.3);
        font-family: 'Share Tech Mono', monospace;
    }

    /* Dataframe styling */
    .stDataFrame {
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }

    /* Buttons */
    .stButton > button {
        background: transparent;
        border: 1px solid var(--accent-cyan);
        color: var(--accent-cyan);
        font-family: 'Share Tech Mono', monospace;
        letter-spacing: 1px;
        border-radius: 4px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background: rgba(0, 212, 255, 0.1);
        border-color: var(--accent-cyan);
        color: var(--accent-cyan);
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background: var(--bg-card) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
    }

    /* Panel box */
    .panel-box {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
    }

    /* Threat level bar */
    .threat-bar-container {
        background: #0a1628;
        border: 1px solid var(--border);
        border-radius: 4px;
        height: 8px;
        margin-top: 8px;
        overflow: hidden;
    }
    .threat-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# CONFIGURATION
# ==================================================
LOG_FILE = "../Logs/ids_detection_logs.csv"

# Try relative paths for flexibility
POSSIBLE_PATHS = [
    "../Logs/ids_detection_logs.csv",
    "Logs/ids_detection_logs.csv",
    "./ids_detection_logs.csv",
]

# ==================================================
# DATA LOADING
# ==================================================
@st.cache_data(ttl=5)
def load_logs():
    for path in POSSIBLE_PATHS:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            return df

    # Demo data if no file found
    st.warning("⚠️ Log file not found. Showing demo data. Make sure `ids_detection_logs.csv` is accessible.")
    now = datetime.now()
    records = []
    statuses = ["BENIGN"] * 80 + ["PortScan"] * 10 + ["DoS"] * 6 + ["SSH-Patator"] * 3 + ["ARP SPOOFING DETECTED"] * 1
    ips = ["192.168.56.1", "192.168.56.108", "192.168.56.200", "10.0.0.5"]
    for i in range(100):
        records.append({
            "Timestamp": now - timedelta(seconds=i*3),
            "Source_IP": random.choice(ips),
            "Packet_Count": random.randint(1, 200),
            "Detection_Status": random.choice(statuses)
        })
    return pd.DataFrame(records)


def get_badge(status):
    s = str(status).upper()
    if "BENIGN" in s:
        return f'<span class="badge-benign">✓ BENIGN</span>'
    elif "PORTSCAN" in s:
        return f'<span class="badge-portscan">⚠ PORT SCAN</span>'
    elif "DOS" in s:
        return f'<span class="badge-dos">🔴 DoS ATTACK</span>'
    elif "SSH" in s:
        return f'<span class="badge-ssh">⚡ SSH-PATATOR</span>'
    elif "ARP" in s:
        return f'<span class="badge-arp">☠ ARP SPOOFING</span>'
    return f'<span class="badge-benign">{status}</span>'


# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 15px 0;'>
        <div style='font-family: Share Tech Mono, monospace; font-size: 1.3rem; color: #00d4ff; letter-spacing: 3px;'>🛡️ SOC-ML</div>
        <div style='font-size: 0.7rem; color: #5a7a99; letter-spacing: 2px; margin-top: 4px;'>INTRUSION DETECTION</div>
    </div>
    <hr style='border-color: #1a3a5c; margin: 10px 0;'>
    """, unsafe_allow_html=True)

    page = st.selectbox("Navigation", ["📊 Dashboard", "📋 Detection Log", "🔍 IP Analysis", "ℹ️ System Info"])

    st.markdown("<hr style='border-color: #1a3a5c;'>", unsafe_allow_html=True)

    auto_refresh = st.toggle("Auto Refresh", value=False)
    refresh_rate = st.slider("Refresh Rate (seconds)", 3, 30, 5) if auto_refresh else 5

    st.markdown("<hr style='border-color: #1a3a5c;'>", unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:0.7rem; color: #5a7a99; font-family: Share Tech Mono, monospace;'>
    <div>MODEL: Random Forest</div>
    <div style='margin-top:5px;'>CLASSES: 4 + ARP</div>
    <div style='margin-top:5px;'>INTERFACE: VirtualBox</div>
    <div style='margin-top:5px;'>WINDOW: 3s</div>
    </div>
    """, unsafe_allow_html=True)

# ==================================================
# AUTO REFRESH
# ==================================================
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()

# ==================================================
# LOAD DATA
# ==================================================
df = load_logs()

# Metrics
total = len(df)
threats = df[df['Detection_Status'] != 'BENIGN']
threat_count = len(threats)
benign_count = total - threat_count
unique_ips = df['Source_IP'].nunique()
threat_pct = (threat_count / total * 100) if total > 0 else 0

status_counts = df['Detection_Status'].value_counts()

# ==================================================
# HEADER
# ==================================================
st.markdown(f"""
<div class="ids-header">
    <div style='display:flex; justify-content:space-between; align-items:center;'>
        <div>
            <h1>🛡️ SOC-ML IDS DASHBOARD</h1>
            <p>HYBRID INTRUSION DETECTION SYSTEM — AI + HEURISTICS + ARP MONITORING</p>
        </div>
        <div style='text-align:right;'>
            <span class="status-live">● LIVE</span>
            <div style='font-family: Share Tech Mono, monospace; font-size:0.75rem; color:#5a7a99; margin-top:8px;'>
                {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================================================
# PAGE: DASHBOARD
# ==================================================
if page == "📊 Dashboard":

    # --- KPI Cards ---
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card cyan">
            <div class="metric-value">{total:,}</div>
            <div class="metric-label">Total Events</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card green">
            <div class="metric-value">{benign_count:,}</div>
            <div class="metric-label">Benign Traffic</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card red">
            <div class="metric-value">{threat_count:,}</div>
            <div class="metric-label">Threats Detected</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card orange">
            <div class="metric-value">{unique_ips}</div>
            <div class="metric-label">Unique IPs</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Charts Row 1 ---
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown('<div class="section-header">// TRAFFIC TIMELINE</div>', unsafe_allow_html=True)

        df_time = df.copy()
        df_time['Minute'] = df_time['Timestamp'].dt.floor('1min')
        timeline = df_time.groupby(['Minute', 'Detection_Status']).size().reset_index(name='Count')

        color_map = {
            'BENIGN': '#00ff88',
            'PortScan': '#ff8c00',
            'DoS': '#ff3366',
            'SSH-Patator': '#ffd700',
            'ARP SPOOFING DETECTED': '#cc44ff'
        }

        fig_timeline = px.area(
            timeline, x='Minute', y='Count', color='Detection_Status',
            color_discrete_map=color_map,
        )
        fig_timeline.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#5a7a99',
            legend=dict(
                bgcolor='rgba(10,22,40,0.8)',
                bordercolor='#1a3a5c',
                borderwidth=1,
                font=dict(color='#e0f0ff', size=11)
            ),
            xaxis=dict(gridcolor='#0d2040', showgrid=True, zeroline=False),
            yaxis=dict(gridcolor='#0d2040', showgrid=True, zeroline=False),
            margin=dict(l=0, r=0, t=10, b=0),
            height=260,
            showlegend=True,
            legend_title_text=''
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-header">// THREAT DISTRIBUTION</div>', unsafe_allow_html=True)

        colors_pie = ['#00ff88', '#ff8c00', '#ff3366', '#ffd700', '#cc44ff']
        fig_pie = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=0.65,
            marker=dict(colors=colors_pie[:len(status_counts)], line=dict(color='#050a0f', width=2)),
            textinfo='label+percent',
            textfont=dict(color='#e0f0ff', size=11),
        )])
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            margin=dict(l=0, r=0, t=10, b=0),
            height=260,
            annotations=[dict(
                text=f'<b>{threat_pct:.1f}%</b><br>THREAT',
                x=0.5, y=0.5, font_size=14,
                font_color='#ff3366',
                showarrow=False
            )]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- Charts Row 2 ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header">// TOP SOURCE IPs</div>', unsafe_allow_html=True)
        top_ips = df.groupby('Source_IP').size().reset_index(name='Events').sort_values('Events', ascending=True).tail(10)
        fig_ips = px.bar(
            top_ips, x='Events', y='Source_IP', orientation='h',
            color_discrete_sequence=['#00d4ff']
        )
        fig_ips.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#5a7a99', xaxis=dict(gridcolor='#0d2040'), yaxis=dict(gridcolor='#0d2040'),
            margin=dict(l=0, r=0, t=5, b=0), height=230,
            xaxis_title='', yaxis_title=''
        )
        st.plotly_chart(fig_ips, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">// PACKETS PER EVENT (DISTRIBUTION)</div>', unsafe_allow_html=True)
        df_pkts = df[df['Packet_Count'] != 'N/A'].copy()
        df_pkts['Packet_Count'] = pd.to_numeric(df_pkts['Packet_Count'], errors='coerce').dropna()
        fig_hist = px.histogram(
            df_pkts, x='Packet_Count', nbins=30,
            color_discrete_sequence=['#00ff88']
        )
        fig_hist.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#5a7a99', xaxis=dict(gridcolor='#0d2040'), yaxis=dict(gridcolor='#0d2040'),
            margin=dict(l=0, r=0, t=5, b=0), height=230,
            bargap=0.05, xaxis_title='Packet Count', yaxis_title='Frequency'
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # --- Recent Alerts ---
    st.markdown('<div class="section-header">// RECENT ALERTS</div>', unsafe_allow_html=True)
    recent_threats = df[df['Detection_Status'] != 'BENIGN'].sort_values('Timestamp', ascending=False).head(5)
    if len(recent_threats) == 0:
        st.markdown('<div class="panel-box" style="color:#00ff88; font-family: Share Tech Mono, monospace; text-align:center;">✓ NO ACTIVE THREATS DETECTED</div>', unsafe_allow_html=True)
    else:
        for _, row in recent_threats.iterrows():
            badge = get_badge(row['Detection_Status'])
            st.markdown(f"""
            <div class="panel-box" style="display:flex; justify-content:space-between; align-items:center; padding:12px 20px;">
                <div style="font-family: Share Tech Mono, monospace; color:#00d4ff;">{row['Source_IP']}</div>
                <div>{badge}</div>
                <div style="font-family: Share Tech Mono, monospace; font-size:0.8rem; color:#5a7a99;">{row['Packet_Count']} pkts</div>
                <div style="font-family: Share Tech Mono, monospace; font-size:0.78rem; color:#5a7a99;">{row['Timestamp'].strftime('%H:%M:%S')}</div>
            </div>
            """, unsafe_allow_html=True)


# ==================================================
# PAGE: DETECTION LOG
# ==================================================
elif page == "📋 Detection Log":
    st.markdown('<div class="section-header">// FULL DETECTION LOG</div>', unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filter_status = st.selectbox("Filter by Status", ["All"] + list(df['Detection_Status'].unique()))
    with col_f2:
        filter_ip = st.selectbox("Filter by IP", ["All"] + list(df['Source_IP'].unique()))
    with col_f3:
        show_n = st.selectbox("Show last N rows", [50, 100, 200, 500, "All"])

    df_filtered = df.copy()
    if filter_status != "All":
        df_filtered = df_filtered[df_filtered['Detection_Status'] == filter_status]
    if filter_ip != "All":
        df_filtered = df_filtered[df_filtered['Source_IP'] == filter_ip]

    df_filtered = df_filtered.sort_values('Timestamp', ascending=False)
    if show_n != "All":
        df_filtered = df_filtered.head(int(show_n))

    # Render with colored badges
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    table_html = '<table style="width:100%; border-collapse:collapse; font-family: Share Tech Mono, monospace; font-size:0.85rem;">'
    table_html += '<tr style="border-bottom:1px solid #1a3a5c; color:#5a7a99;">'
    table_html += '<th style="padding:10px; text-align:left;">TIMESTAMP</th>'
    table_html += '<th style="padding:10px; text-align:left;">SOURCE IP</th>'
    table_html += '<th style="padding:10px; text-align:left;">PACKETS</th>'
    table_html += '<th style="padding:10px; text-align:left;">STATUS</th>'
    table_html += '</tr>'

    for _, row in df_filtered.iterrows():
        badge = get_badge(row['Detection_Status'])
        table_html += f'''<tr style="border-bottom:1px solid #0d1f35;">
            <td style="padding:9px 10px; color:#5a7a99;">{row["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")}</td>
            <td style="padding:9px 10px; color:#00d4ff;">{row["Source_IP"]}</td>
            <td style="padding:9px 10px; color:#e0f0ff;">{row["Packet_Count"]}</td>
            <td style="padding:9px 10px;">{badge}</td>
        </tr>'''

    table_html += '</table>'
    st.markdown(table_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div style="font-family: Share Tech Mono, monospace; font-size:0.75rem; color:#5a7a99; margin-top:10px;">Showing {len(df_filtered):,} records</div>', unsafe_allow_html=True)


# ==================================================
# PAGE: IP ANALYSIS
# ==================================================
elif page == "🔍 IP Analysis":
    st.markdown('<div class="section-header">// IP THREAT ANALYSIS</div>', unsafe_allow_html=True)

    selected_ip = st.selectbox("Select IP Address", df['Source_IP'].unique())
    ip_df = df[df['Source_IP'] == selected_ip]

    c1, c2, c3 = st.columns(3)
    ip_threats = ip_df[ip_df['Detection_Status'] != 'BENIGN']
    threat_types = ip_df['Detection_Status'].value_counts()

    with c1:
        st.markdown(f"""<div class="metric-card cyan">
            <div class="metric-value">{len(ip_df)}</div>
            <div class="metric-label">Total Events</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card red">
            <div class="metric-value">{len(ip_threats)}</div>
            <div class="metric-label">Threats</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        avg_pkts = pd.to_numeric(ip_df['Packet_Count'], errors='coerce').mean()
        st.markdown(f"""<div class="metric-card orange">
            <div class="metric-value">{avg_pkts:.0f}</div>
            <div class="metric-label">Avg Packets</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">// ACTIVITY TIMELINE</div>', unsafe_allow_html=True)
        ip_time = ip_df.copy()
        ip_time['Minute'] = ip_time['Timestamp'].dt.floor('1min')
        ip_timeline = ip_time.groupby(['Minute', 'Detection_Status']).size().reset_index(name='Count')
        fig = px.bar(ip_timeline, x='Minute', y='Count', color='Detection_Status',
                     color_discrete_map={'BENIGN': '#00ff88', 'PortScan': '#ff8c00', 'DoS': '#ff3366', 'SSH-Patator': '#ffd700'})
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font_color='#5a7a99', height=250,
                          xaxis=dict(gridcolor='#0d2040'), yaxis=dict(gridcolor='#0d2040'),
                          margin=dict(l=0, r=0, t=5, b=0), legend_title_text='')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">// STATUS BREAKDOWN</div>', unsafe_allow_html=True)
        fig2 = px.pie(values=threat_types.values, names=threat_types.index,
                      color_discrete_sequence=['#00ff88', '#ff8c00', '#ff3366', '#ffd700', '#cc44ff'],
                      hole=0.5)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           font_color='#e0f0ff', height=250, margin=dict(l=0, r=0, t=5, b=0))
        st.plotly_chart(fig2, use_container_width=True)


# ==================================================
# PAGE: SYSTEM INFO
# ==================================================
elif page == "ℹ️ System Info":
    st.markdown('<div class="section-header">// SYSTEM INFORMATION</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="panel-box">
            <div style="font-family: Share Tech Mono, monospace; color: #00d4ff; margin-bottom: 15px; font-size:0.9rem;">🤖 ML MODEL</div>
            <table style="width:100%; font-size:0.85rem; font-family: Share Tech Mono, monospace;">
                <tr><td style="color:#5a7a99; padding:6px 0;">Algorithm</td><td style="color:#e0f0ff;">Random Forest</td></tr>
                <tr><td style="color:#5a7a99; padding:6px 0;">Estimators</td><td style="color:#e0f0ff;">100 Trees</td></tr>
                <tr><td style="color:#5a7a99; padding:6px 0;">Max Depth</td><td style="color:#e0f0ff;">25</td></tr>
                <tr><td style="color:#5a7a99; padding:6px 0;">Class Weight</td><td style="color:#e0f0ff;">Balanced</td></tr>
                <tr><td style="color:#5a7a99; padding:6px 0;">Dataset</td><td style="color:#e0f0ff;">CIC-IDS-2017</td></tr>
                <tr><td style="color:#5a7a99; padding:6px 0;">Features</td><td style="color:#e0f0ff;">10 Features</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="panel-box">
            <div style="font-family: Share Tech Mono, monospace; color: #00d4ff; margin-bottom: 15px; font-size:0.9rem;">🛡️ DETECTION CLASSES</div>
            <table style="width:100%; font-size:0.85rem; font-family: Share Tech Mono, monospace;">
                <tr><td style="padding:6px 0;"><span class="badge-benign">✓ BENIGN</span></td><td style="color:#5a7a99; padding:6px 10px;">Normal traffic</td></tr>
                <tr><td style="padding:6px 0;"><span class="badge-portscan">⚠ PORT SCAN</span></td><td style="color:#5a7a99; padding:6px 10px;">Port scanning activity</td></tr>
                <tr><td style="padding:6px 0;"><span class="badge-dos">🔴 DoS</span></td><td style="color:#5a7a99; padding:6px 10px;">Denial of Service</td></tr>
                <tr><td style="padding:6px 0;"><span class="badge-ssh">⚡ SSH-PATATOR</span></td><td style="color:#5a7a99; padding:6px 10px;">SSH Brute Force</td></tr>
                <tr><td style="padding:6px 0;"><span class="badge-arp">☠ ARP SPOOF</span></td><td style="color:#5a7a99; padding:6px 10px;">Layer 2 ARP Spoofing</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="panel-box">
        <div style="font-family: Share Tech Mono, monospace; color: #00d4ff; margin-bottom: 15px; font-size:0.9rem;">⚙️ DETECTION PIPELINE</div>
        <div style="display:flex; gap:10px; align-items:center; font-family: Share Tech Mono, monospace; font-size:0.82rem; flex-wrap:wrap;">
            <div style="background:#0a1628; border:1px solid #1a3a5c; padding:8px 15px; border-radius:4px; color:#00d4ff;">SNIFF PACKETS</div>
            <div style="color:#5a7a99;">→</div>
            <div style="background:#0a1628; border:1px solid #1a3a5c; padding:8px 15px; border-radius:4px; color:#00d4ff;">ARP LAYER CHECK</div>
            <div style="color:#5a7a99;">→</div>
            <div style="background:#0a1628; border:1px solid #1a3a5c; padding:8px 15px; border-radius:4px; color:#00d4ff;">FEATURE EXTRACTION</div>
            <div style="color:#5a7a99;">→</div>
            <div style="background:#0a1628; border:1px solid #1a3a5c; padding:8px 15px; border-radius:4px; color:#00d4ff;">SCALER TRANSFORM</div>
            <div style="color:#5a7a99;">→</div>
            <div style="background:#0a1628; border:1px solid #1a3a5c; padding:8px 15px; border-radius:4px; color:#00d4ff;">RF PREDICT</div>
            <div style="color:#5a7a99;">→</div>
            <div style="background:#0a1628; border:1px solid #1a3a5c; padding:8px 15px; border-radius:4px; color:#00d4ff;">HEURISTICS</div>
            <div style="color:#5a7a99;">→</div>
            <div style="background:#0a1628; border:1px solid #ff3366; padding:8px 15px; border-radius:4px; color:#ff3366;">LOG TO CSV</div>
        </div>
    </div>
    """, unsafe_allow_html=True)