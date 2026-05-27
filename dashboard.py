import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from fault_detection import detect_faults
from simulator import run_dynamic_session

# ── Brand colors ──────────────────────────────
YELLOW  = "#F5C518"
WHITE   = "#FFFFFF"
DARK    = "#0E0E0E"
GRAY    = "#1C1C1C"
DIMGRAY = "#888888"

st.set_page_config(
    page_title="Sunnybotics Field Monitor",
    page_icon="☀",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────
st.markdown(f"""
    <style>
        body, .stApp {{ background-color: {DARK}; }}
        h1, h2, h3 {{ color: {WHITE}; font-family: 'Arial', sans-serif; letter-spacing: -0.5px; }}
        .stMarkdown p {{ color: {DIMGRAY}; font-size: 14px; }}
        .stButton > button {{
            background-color: {YELLOW};
            color: black;
            font-weight: 700;
            border: none;
            padding: 10px 24px;
            border-radius: 4px;
            font-size: 14px;
            letter-spacing: 0.5px;
        }}
        .stButton > button:hover {{ background-color: #d4a800; }}
        .alert-card {{
            background-color: {GRAY};
            border-left: 3px solid {YELLOW};
            padding: 12px 16px;
            margin-bottom: 12px;
            border-radius: 4px;
        }}
        .alert-name {{
            color: {YELLOW};
            font-weight: 700;
            font-size: 13px;
            letter-spacing: 1px;
        }}
        .alert-time {{
            color: {DIMGRAY};
            font-size: 11px;
            margin-top: 4px;
        }}
        div[data-testid="stStatusWidget"] {{ display: none; }}
        div[data-testid="stToast"] {{
            background-color: rgba(245, 197, 24, 0.15);
            border: 1px solid #F5C518;
            border-radius: 4px;
            color: #F5C518;
            font-weight: 700;
            font-size: 13px;
            letter-spacing: 1px;
        }}
    </style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────
st.markdown(f"<h1 style='font-size:28px; margin-bottom:0'>SUNNYBOTICS</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:{DIMGRAY}; margin-top:0; font-size:13px; letter-spacing:2px'>FIELD MONITOR</p>", unsafe_allow_html=True)
st.markdown("<hr style='border-color:#222; margin: 8px 0 20px 0'>", unsafe_allow_html=True)

# ── Popup slot — defined before button so it can be cleared ──
popup_slot = st.empty()

# ── Run Simulation Button ─────────────────────
if st.button("RUN NEW SIMULATION"):
    popup_slot.empty()
    st.session_state.df = run_dynamic_session()
    st.session_state.df = detect_faults(st.session_state.df)

if "df" not in st.session_state:
    st.markdown(f"<p style='color:{DIMGRAY}'>Press RUN NEW SIMULATION to begin.</p>", unsafe_allow_html=True)
    st.stop()

df = st.session_state.df

# ── Layout ────────────────────────────────────
col_charts, col_alerts = st.columns([3, 1])

with col_charts:
    st.markdown(f"<h3 style='font-size:13px; letter-spacing:2px; color:{DIMGRAY}'>LIVE TELEMETRY</h3>", unsafe_allow_html=True)
    chart_slot  = st.empty()
    status_slot = st.empty()

with col_alerts:
    st.markdown(f"<h3 style='font-size:13px; letter-spacing:2px; color:{DIMGRAY}'>ACTIVE ALERTS</h3>", unsafe_allow_html=True)
    alert_slot = st.empty()

# ── Live Playback ─────────────────────────────
alerts_seen = []

for i in range(1, len(df) + 1):
    current = df.iloc[:i]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=current["timestamp"], y=current["battery_pct"],
        name="Battery %", line=dict(color="#F5C518", width=1.5)))

    fig.add_trace(go.Scatter(
        x=current["timestamp"], y=current["brush_rpm"] / 10,
        name="Brush RPM / 10", line=dict(color="#FFFFFF", width=1.5)))

    fig.add_trace(go.Scatter(
        x=current["timestamp"], y=current["motor_temp_C"],
        name="Motor Temp C", line=dict(color="#888888", width=1.5)))

    fig.add_trace(go.Scatter(
        x=current["timestamp"], y=current["tank_level_L"],
        name="Tank Level L", line=dict(color="#444444", width=1.5)))

    fig.update_layout(
        height=420,
        paper_bgcolor="#0E0E0E",
        plot_bgcolor="#0E0E0E",
        font=dict(color="#888888", size=11),
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(
            orientation="h",
            font=dict(size=10, color="#888888"),
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(showgrid=False, color="#444"),
        yaxis=dict(showgrid=True, gridcolor="#1C1C1C", color="#444"),
    )

    chart_slot.plotly_chart(fig, use_container_width=True)

    row = df.iloc[i - 1]
    alert_names = [a[0] for a in alerts_seen]

    if pd.notna(row["alert"]) and row["alert"] not in alert_names:
        alerts_seen.append((row["alert"], str(row["timestamp"])[:19]))
        st.toast(f"! ALERT: {row['alert']}")

        alert_html = ""
        for a, t_val in alerts_seen:
            alert_html += f"""
            <div class='alert-card'>
                <div class='alert-name'>{a}</div>
                <div class='alert-time'>{t_val}</div>
            </div>
            """
        alert_slot.markdown(alert_html, unsafe_allow_html=True)

    status_slot.markdown(
        f"<p style='color:{DIMGRAY}; font-size:18px; letter-spacing:2px; margin-top:8px'>"
        f"STATE: <span style='color:{YELLOW}; font-weight:700'>{row['state']}</span> &nbsp;|&nbsp; "
        f"{str(row['timestamp'])[:19]}</p>",
        unsafe_allow_html=True
    )

    time.sleep(0.05)

# ── Simulation complete popup ─────────────────
total_errors = len(alerts_seen)
popup_slot.markdown(f"""
    <div style='
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: rgba(14, 14, 14, 0.97);
        border: 1px solid {YELLOW};
        border-radius: 6px;
        padding: 48px 64px;
        text-align: center;
        z-index: 9999;
    '>
        <p style='color:{DIMGRAY}; font-size:11px; letter-spacing:3px; margin:0 0 12px 0'>SIMULATION COMPLETE</p>
        <p style='color:{YELLOW}; font-size:48px; font-weight:700; margin:0; line-height:1'>{total_errors}</p>
        <p style='color:{WHITE}; font-size:14px; letter-spacing:2px; margin:8px 0 0 0'>FAULT{"S" if total_errors != 1 else ""} DETECTED</p>
    </div>
""", unsafe_allow_html=True)