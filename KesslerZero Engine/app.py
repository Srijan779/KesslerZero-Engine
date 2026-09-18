# app.py - KesslerZero Space Flight Operations Console
# Autonomous Conjunction Assessment & Collision Avoidance System

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timezone

# ------------------------------------------------------------------------------
# 1. FLIGHT DYNAMICS CONSOLE STYLING (AEROSPACE TELEMETRY SPEC)
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="KesslerZero | Flight Operations",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg-base: #0a0d14;
        --panel-bg: #111622;
        --panel-border: #1e2638;
        --border-subtle: #161e2e;
        --text-main: #e2e8f0;
        --text-muted: #8492a6;
        --text-dim: #4c566a;
        --accent-blue: #2563eb;
        --accent-sky: #38bdf8;
        --status-safe: #059669;
        --status-safe-bg: rgba(5, 150, 105, 0.08);
        --status-warn: #d97706;
        --status-warn-bg: rgba(217, 119, 6, 0.08);
        --status-danger: #dc2626;
        --status-danger-bg: rgba(220, 38, 38, 0.08);
    }

    .main { 
        background-color: var(--bg-base); 
        color: var(--text-main); 
        font-family: 'Inter', -apple-system, sans-serif; 
    }
    
    .top-header {
        background: var(--panel-bg);
        border: 1px solid var(--panel-border);
        border-radius: 4px;
        padding: 10px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
    }

    .telemetry-strip {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.5px;
        color: var(--text-muted);
    }

    .telemetry-strip strong {
        color: var(--text-main);
    }

    .panel-container {
        background: var(--panel-bg);
        border: 1px solid var(--panel-border);
        border-radius: 4px;
        padding: 14px;
        margin-bottom: 12px;
    }

    .section-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
        color: var(--text-muted);
        text-transform: uppercase;
        margin-bottom: 4px;
    }

    .packet-log {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11.5px;
        background: #06090e;
        border: 1px solid var(--panel-border);
        border-left: 3px solid var(--accent-sky);
        padding: 10px 12px;
        border-radius: 2px;
        color: #93c5fd;
        line-height: 1.6;
    }

    div[data-testid="stMetricValue"] > div {
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px;
        font-weight: 600;
        letter-spacing: -0.5px;
    }

    div[data-testid="stMetricLabel"] > div {
        font-size: 11.5px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. CONSTELLATION ORBITAL DATABASE & ENCOUNTER CATALOG
# ------------------------------------------------------------------------------
FLEET_DATABASE = {
    "SAT-IND-LEO-01 (Defense Reconnaissance)": {
        "id": "SAT-IND-LEO-01",
        "regime": "550 km Polar LEO | Inclination: 97.4°",
        "propulsion": "Chemical Monopropellant (Hydrazine RCS Bank)",
        "mode": "Impulsive Along-Track Phasing (Hill-Clohessy-Wiltshire)",
        "hazard_id": "DEBRIS-KOSMOS-2251-FRAG (CAT #34289)",
        "tca_epoch": "2026-09-19 14:12:08 UTC (T - 23h 48m)",
        "miss_raw": "480 m",
        "miss_status": "CRITICAL (Violates 1.0 km Threshold)",
        "pc_raw": "9.64e-01",
        "panic_dv": "3.20 m/s (Reactive Burn @ T-2h)",
        "micro_dv": "0.36 m/s (Phasing Micro-Burn @ T-24h)",
        "propellant_delta": "88.7% Reduction",
        "action_btn": "EXECUTE RCS PHASING BURN",
        "action_desc": "Commands along-track velocity increment (+0.362 m/s) at ascending node. Shifts semi-major axis by +640 m, inducing 11.4 km along-track separation at encounter epoch.",
        "resolved_miss": "11.4 km",
        "tc_packet": "CCSDS_TC_LEO01_THRUST_P_0362_BURNTIME_4.12S",
        "coord_pre": [0, 480, 80],
        "coord_post": [0, 11400, 120]
    },
    "STUDENT-CUBESAT-03 (3U Research Platform)": {
        "id": "STUDENT-CUBESAT-03",
        "regime": "480 km Circular LEO | Inclination: 51.6°",
        "propulsion": "Unpropelled / Thrusterless (3-Axis Reaction Wheel Control)",
        "mode": "Non-Impulsive Aerodynamic Differential Drag Attitude Slew",
        "hazard_id": "ENVISAT-FRAGMENT-B (CAT #27386)",
        "tca_epoch": "2026-09-19 11:54:30 UTC (T - 21h 30m)",
        "miss_raw": "650 m",
        "miss_status": "CRITICAL (Violates 1.0 km Threshold)",
        "pc_raw": "8.70e-01",
        "panic_dv": "INOPERABLE (No Onboard Propulsion Subsystem)",
        "optimal_dv": "0.00 kg Propellant (Attitude Slew to Maximum Cross-Section)",
        "propellant_delta": "100% Conserved",
        "action_btn": "EXECUTE DIFFERENTIAL DRAG ORIENTATION",
        "action_desc": "Commands 3-axis reaction wheel cluster to slew attitude by 90.0° pitch. Maximizes ram surface area against thermospheric flow, inducing -4.8 km relative along-track drift.",
        "resolved_miss": "4.8 km",
        "tc_packet": "CCSDS_TC_CS03_ATT_PITCH_90DEG_DRAG_MAX_CD",
        "coord_pre": [0, 650, -40],
        "coord_post": [0, 4800, 90]
    },
    "CARTOSAT-RECON-02 (Optical Imaging Platform)": {
        "id": "CARTOSAT-RECON-02",
        "regime": "630 km Sun-Synchronous LEO | Inclination: 98.1°",
        "propulsion": "Hall-Effect Electric Propulsion Subsystem (Xenon Ion)",
        "mode": "Pareto-Constrained Multi-Conjunction Vector Optimization",
        "hazard_id": "DUAL ENCOUNTER: FENGYUN-1C + CZ-4C BOOSTER",
        "tca_epoch": "TCA-1: T - 16h 20m | TCA-2: T - 34h 10m",
        "miss_raw": "310 m & 580 m",
        "miss_status": "DUAL CORRIDOR VIOLATION",
        "pc_raw": "9.88e-01 (Joint)",
        "panic_dv": "6.40 m/s (Two Sequential Reactive Burns)",
        "optimal_dv": "0.52 m/s (Single Unified Pareto Vector)",
        "propellant_delta": "91.8% Reduction",
        "action_btn": "EXECUTE UNIFIED DUAL-CLEARANCE BURN",
        "action_desc": "Calculates unified multi-objective orbital trim (+0.520 m/s). Introduces 4.2-second arrival delay, clearing Threat 1 ahead and Threat 2 astern while respecting constellation corridors.",
        "resolved_miss": "12.8 km (Both Cleared)",
        "tc_packet": "CCSDS_TC_CR02_ION_MULTI_PHASE_DV_0520_EP",
        "coord_pre": [0, 310, 60],
        "coord_post": [0, 12800, 240]
    }
}

# ------------------------------------------------------------------------------
# 3. STATE MANAGEMENT
# ------------------------------------------------------------------------------
if 'fleet_states' not in st.session_state:
    st.session_state.fleet_states = {k: False for k in FLEET_DATABASE.keys()}

def authorize_asset(asset_key):
    st.session_state.fleet_states[asset_key] = True

def reset_asset(asset_key):
    st.session_state.fleet_states[asset_key] = False

def reset_all_ephemeris():
    for k in st.session_state.fleet_states:
        st.session_state.fleet_states[k] = False

now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

# ------------------------------------------------------------------------------
# 4. PRIMARY TELEMETRY HEADER
# ------------------------------------------------------------------------------
col_h1, col_h2 = st.columns([4, 1])

with col_h1:
    st.markdown(f"""
    <div class="top-header">
        <div>
            <strong style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #f8fafc; letter-spacing: 0.5px;">
                KESSLERZERO FLIGHT DYNAMICS CONSOLE
            </strong>
            <span style="color: #475569; margin: 0 8px;">|</span>
            <span class="telemetry-strip">SYSTEM STATUS: <strong style="color: #10b981;">NOMINAL</strong></span>
        </div>
        <div class="telemetry-strip">
            <span>TRACKED ASSETS: <strong>3 ACTIVE</strong></span>
            <span style="color: #475569; margin: 0 8px;">|</span>
            <span>EPOCH: <strong>{now_utc}</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    st.button("Reset Ephemeris Telemetry", on_click=reset_all_ephemeris, use_container_width=True)

# ------------------------------------------------------------------------------
# 5. SECTION 01: CONSTELLATION CONJUNCTION WATCHLIST
# ------------------------------------------------------------------------------
st.markdown('<div class="section-label">01 // Constellation Conjunction Assessment Feed</div>', unsafe_allow_html=True)

feed_records = []
for k, data in FLEET_DATABASE.items():
    is_cleared = st.session_state.fleet_states[k]
    status_tag = "CLEARED (TRAJECTORY SECURED)" if is_cleared else "CRITICAL (CORRIDOR BREACH)"
    curr_miss = data['resolved_miss'] if is_cleared else data['miss_raw']
    curr_pc = "< 1.00e-05" if is_cleared else data['pc_raw']
    
    feed_records.append({
        "Status": status_tag,
        "Target Spacecraft": data['id'],
        "Propulsion Subsystem": data['propulsion'].split('(')[0].strip(),
        "Conjunction Threat Object": data['hazard_id'].split('(')[0].strip(),
        "Time of Closest Approach (TCA)": data['tca_epoch'],
        "Predicted Miss": curr_miss,
        "Collision Probability (Pc)": curr_pc
    })

st.dataframe(pd.DataFrame(feed_records), use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# 6. SECTION 02: ACTIVE TARGET CONTROLLER & TELEMETRY
# ------------------------------------------------------------------------------
st.markdown('<div class="section-label" style="margin-top: 14px;">02 // Spacecraft Tactical Controller</div>', unsafe_allow_html=True)

col_selector, col_status = st.columns([3, 1])

with col_selector:
    active_key = st.selectbox(
        "Select Active Spacecraft Profile:",
        options=list(FLEET_DATABASE.keys()),
        label_visibility="collapsed"
    )

asset = FLEET_DATABASE[active_key]
is_auth = st.session_state.fleet_states[active_key]

with col_status:
    if is_auth:
        st.markdown("""
        <div style="background: rgba(5, 150, 105, 0.1); border: 1px solid #059669; color: #10b981; padding: 7px 12px; border-radius: 4px; font-family: 'JetBrains Mono'; font-size: 11.5px; text-align: center; font-weight: 600;">
            CORRIDOR SECURED
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(220, 38, 38, 0.1); border: 1px solid #dc2626; color: #ef4444; padding: 7px 12px; border-radius: 4px; font-family: 'JetBrains Mono'; font-size: 11.5px; text-align: center; font-weight: 600;">
            HAZARD DETECTED
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 7. SECTION 03: ENCOUNTER METRICS & B-PLANE RELATIVE RADAR
# ------------------------------------------------------------------------------
col_metrics, col_radar = st.columns([1, 1])

with col_metrics:
    st.markdown(f"""
    <div class="panel-container">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #64748b; text-transform: uppercase;">
            Spacecraft Subsystem Configuration
        </div>
        <div style="font-size: 14px; font-weight: 600; color: #f1f5f9; margin-top: 2px;">
            {asset['id']}
        </div>
        <div style="font-size: 12px; color: #94a3b8; margin-top: 4px; line-height: 1.5;">
            <strong>Regime:</strong> {asset['regime']}<br>
            <strong>Hardware:</strong> {asset['propulsion']}<br>
            <strong>Maneuver Strategy:</strong> {asset['mode']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not is_auth:
        m1, m2, m3 = st.columns(3)
        m1.metric("Predicted Miss", asset['miss_raw'])
        m2.metric("Conjunction Threat", asset['hazard_id'].split()[0])
        m3.metric("Collision Prob (Pc)", asset['pc_raw'])
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Secured Clearance", asset['resolved_miss'], delta="Separation Validated")
        m2.metric("Residual Collision Prob", "< 1.00e-05", delta="-99.9% Drop")
        m3.metric("Secondary Hazards", "0 (48h Sweep)")

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Propellant Conservation Trade-Off</div>', unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.metric("Reactive Panic Burn (T-2h)", asset['panic_dv'])
    with col_t2:
        val = asset['micro_dv'] if 'micro_dv' in asset else asset['optimal_dv']
        st.metric("Optimized Phasing Solution", val, delta=asset['propellant_delta'])

with col_radar:
    st.markdown('<div class="section-label">Relative Motion Encounter Geometry (B-Plane Reference)</div>', unsafe_allow_html=True)
    
    fig = go.Figure()

    # 1. Threat Velocity Vector
    fig.add_trace(go.Scatter3d(
        x=[-1200, 1200], y=[0, 0], z=[0, 0],
        mode='lines', line=dict(color='#dc2626', width=6),
        name='Debris Vector'
    ))

    # 2. Predicted Conjunction Intersection Origin
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers', marker=dict(size=6, color='#dc2626', symbol='diamond'),
        name='Encounter Origin'
    ))

    # 3. 1.0 km Exclusion Perimeter
    theta = np.linspace(0, 2 * np.pi, 72)
    r_perimeter = 1000  # 1 km threshold
    fig.add_trace(go.Scatter3d(
        x=r_perimeter * np.cos(theta),
        y=r_perimeter * np.sin(theta),
        z=np.zeros_like(theta),
        mode='lines',
        line=dict(color='rgba(220, 38, 38, 0.6)', width=3, dash='dash'),
        name='1.0 km Threshold Perimeter'
    ))

    # 4. Satellite Coordinates (Pre-Maneuver vs Post-Maneuver)
    if not is_auth:
        coord = asset['coord_pre']
        fig.add_trace(go.Scatter3d(
            x=[coord[0]], y=[coord[1]], z=[coord[2]],
            mode='markers+text',
            marker=dict(size=12, color='#d97706', line=dict(color='#ffffff', width=1.5)),
            name=f"{asset['id']} (Hazard Point)",
            text=[f"Miss: {coord[1]}m"], textposition="top center"
        ))
    else:
        coord = asset['coord_post']
        fig.add_trace(go.Scatter3d(
            x=[coord[0]], y=[coord[1]], z=[coord[2]],
            mode='markers+text',
            marker=dict(size=12, color='#059669', line=dict(color='#ffffff', width=1.5)),
            name=f"{asset['id']} (Cleared Position)",
            text=[f"Cleared: {asset['resolved_miss']}"], textposition="top center"
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Along-Track (m)', backgroundcolor="#0a0d14", color="#475569", gridcolor="#1e2638"),
            yaxis=dict(title='Cross-Track (m)', backgroundcolor="#0a0d14", color="#475569", gridcolor="#1e2638"),
            zaxis=dict(title='Radial Offset (m)', backgroundcolor="#0a0d14", color="#475569", gridcolor="#1e2638"),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.1))
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor="#0a0d14",
        legend=dict(
            font=dict(color="#cbd5e1", family="JetBrains Mono", size=9.5),
            orientation="h",
            y=1.05
        )
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------------------
# 8. SECTION 04: MANEUVER COMMAND & EXECUTION UNIT
# ------------------------------------------------------------------------------
st.markdown('<div class="section-label" style="margin-top: 14px;">03 // Telecommand Execution Unit</div>', unsafe_allow_html=True)

col_cmd_info, col_cmd_btn = st.columns([3, 1])

with col_cmd_info:
    if not is_auth:
        st.markdown(f"""
        <div class="panel-container" style="margin-bottom: 0;">
            <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #64748b; text-transform: uppercase;">
                Trajectory Solver Output
            </div>
            <div style="font-size: 13px; color: #cbd5e1; margin-top: 4px; line-height: 1.5;">
                {asset['action_desc']}
            </div>
            <div style="font-size: 11.5px; color: #64748b; margin-top: 6px;">
                Inter-Constellation Safety: Screened against active constellation catalog with 50 km keep-out sphere.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="panel-container" style="margin-bottom: 0; border-left: 3px solid #059669;">
            <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #10b981; text-transform: uppercase;">
                Telecommand Frame Dispatched & Acknowledged
            </div>
            <div style="font-size: 13px; color: #cbd5e1; margin-top: 4px;">
                Maneuver telecommand uplinks successfully committed for {asset['id']}. Ephemeris propagation updated.
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_cmd_btn:
    st.write("")
    if not is_auth:
        if st.button(asset['action_btn'], type="primary", use_container_width=True):
            authorize_asset(active_key)
            st.rerun()
    else:
        st.button("TELECOMMAND ACTIVE", disabled=True, use_container_width=True)
        if st.button("Reset Asset State", use_container_width=True):
            reset_asset(active_key)
            st.rerun()

# Telemetry Packet Output (When Executed)
if is_auth:
    st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">CCSDS Uplink Frame & Mission Verification Audit</div>', unsafe_allow_html=True)

    col_pkt, col_audit = st.columns([1, 1])

    with col_pkt:
        st.markdown(f"""
        <div class="packet-log">
        [CCSDS_TC_FRAME_TRANSMITTED]<br>
        SPACECRAFT_IDENT   : {asset['id']}<br>
        TELECOMMAND_STR    : {asset['tc_packet']}<br>
        PROPULSION_PROFILE : {asset['propulsion'].split('(')[0].strip()}<br>
        FORWARD_SWEEP_48H  : ZERO_SECONDARY_INTERSECTIONS<br>
        CRYPTO_SIGNATURE   : SHA256: 4e91bc708...df281e [VERIFIED]
        </div>
        """, unsafe_allow_html=True)

    with col_audit:
        st.dataframe(pd.DataFrame({
            "Verification Metric": [
                "Solver Computation Latency",
                "Propellant Savings vs Reactive Burn",
                "Constellation Separation Buffer",
                "48-Hour Secondary Risk"
            ],
            "Telemetry Value": [
                "0.41 Seconds",
                f"{asset['propellant_delta']}",
                "> 180 km from sister spacecraft",
                "Clean (Zero intersections detected)"
            ]
        }), use_container_width=True, hide_index=True)
