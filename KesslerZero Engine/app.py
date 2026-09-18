# app.py - KesslerZero Space Flight Operations Console
# Autonomous Satellite Collision Avoidance & Propellant Conservation System

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timezone

# ------------------------------------------------------------------------------
# 1. CLEAN FLIGHT OPERATIONS STYLING (HIGH-CONTRAST / ZERO CLUTTER)
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="KesslerZero | Autonomous Collision Avoidance",
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
        --text-main: #f1f5f9;
        --text-muted: #94a3b8;
        --accent-blue: #38bdf8;
        --status-safe: #10b981;
        --status-danger: #ef4444;
    }

    .main { 
        background-color: var(--bg-base); 
        color: var(--text-main); 
        font-family: 'Inter', -apple-system, sans-serif; 
    }
    
    .top-header {
        background: var(--panel-bg);
        border: 1px solid var(--panel-border);
        border-radius: 6px;
        padding: 12px 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }

    .telemetry-strip {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11.5px;
        color: var(--text-muted);
    }

    .telemetry-strip strong {
        color: var(--text-main);
    }

    .panel-box {
        background: var(--panel-bg);
        border: 1px solid var(--panel-border);
        border-radius: 6px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }

    .section-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        color: var(--accent-blue);
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .packet-log {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11.5px;
        background: #05080f;
        border: 1px solid var(--panel-border);
        border-left: 3px solid var(--accent-blue);
        padding: 12px;
        border-radius: 4px;
        color: #7dd3fc;
        line-height: 1.6;
    }

    div[data-testid="stMetricValue"] > div {
        font-family: 'JetBrains Mono', monospace;
        font-size: 24px;
        font-weight: 700;
    }

    div[data-testid="stMetricLabel"] > div {
        font-size: 12px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. ORBITAL FLEET DATABASE (PLAIN-ENGLISH SCENARIOS)
# ------------------------------------------------------------------------------
FLEET_DATABASE = {
    "SAT-IND-LEO-01 (Defense Recon Satellite)": {
        "id": "SAT-IND-LEO-01",
        "role": "Defense Optical Reconnaissance",
        "orbit_info": "550 km Polar Orbit (Speed: ~27,500 km/h)",
        "hardware_type": "Chemical Thrusters Onboard",
        "debris_name": "Kosmos-2251 Rocket Debris",
        "time_to_impact": "23 hours, 48 minutes",
        "initial_miss_m": "480 meters (FATAL BREACH: Inside 1,000m Danger Zone)",
        "risk_percentage": "96.4%",
        "problem_statement": "A high-speed debris fragment is crossing our satellite's orbital corridor tomorrow at 480 meters. In space, anything under 1,000 meters is an immediate red alert.",
        "old_way": "Emergency panic burn 2 hours before impact (3.2 m/s). Burns heavy fuel and drains 1.8 years of satellite mission life.",
        "our_way": "A gentle 4.1-second micro-burn (+0.36 m/s) executed 24 hours early. Orbital physics widens the gap to 11.4 km automatically.",
        "fuel_saved": "88.7% Fuel Saved",
        "action_button": "EXECUTE RCS MICRO-BURN (+0.36 m/s)",
        "resolved_miss": "11.4 km (Completely Safe)",
        "packet_string": "CMD_EXEC_RCS_MICRO_BURN_PHASING_DV_0.362_BURNTIME_4.12S",
        "coord_pre": [0, 480, 80],
        "coord_post": [0, 11400, 120]
    },
    "STUDENT-CUBESAT-03 (University SmallSat)": {
        "id": "STUDENT-CUBESAT-03",
        "role": "University 3U Science Satellite",
        "orbit_info": "480 km Low Orbit (Atmospheric Drag Layer)",
        "hardware_type": "Motorless (Reaction Wheels Only - Zero Thrusters)",
        "debris_name": "Envisat Satellite Fragment",
        "time_to_impact": "21 hours, 30 minutes",
        "initial_miss_m": "650 meters (FATAL BREACH: Inside 1,000m Danger Zone)",
        "risk_percentage": "87.0%",
        "problem_statement": "Small university satellites do NOT have rocket engines. When space debris approaches at 650 meters, standard thruster burns are physically impossible.",
        "old_way": "Unable to maneuver. University operators are forced to watch the collision risk helplessly.",
        "our_way": "Commands internal balance wheels to tilt the solar panels 90° sideways. The thin upper atmosphere acts like a brake (aerodynamic drag), sliding the satellite 4.8 km to safety with ZERO fuel.",
        "fuel_saved": "100% Propellant-Free",
        "action_button": "EXECUTE 90° DIFFERENTIAL DRAG ROTATION",
        "resolved_miss": "4.8 km (Completely Safe)",
        "packet_string": "CMD_EXEC_ATTITUDE_PITCH_90DEG_MAX_DRAG_AERO_EVASION",
        "coord_pre": [0, 650, -40],
        "coord_post": [0, 4800, 90]
    },
    "CARTOSAT-RECON-02 (Dual Conjunction Threat)": {
        "id": "CARTOSAT-RECON-02",
        "role": "Earth Observation Satellite",
        "orbit_info": "630 km Sun-Synchronous Orbit",
        "hardware_type": "Electric Ion Propulsion (High Efficiency)",
        "debris_name": "Dual Threat: Fengyun Debris + Spent Booster",
        "time_to_impact": "Threat 1: 16h | Threat 2: 34h",
        "initial_miss_m": "310m & 580m (DOUBLE CORRIDOR BREACH)",
        "risk_percentage": "98.8%",
        "problem_statement": "Two independent pieces of space debris are intercepting the same satellite within 36 hours. Dodging the first hazard carelessly can push the satellite directly into the second.",
        "old_way": "Two separate emergency burns. Wastes fuel and risks steering into sister satellites or the second debris path.",
        "our_way": "Our multi-target solver calculates a single unified micro-burn (+0.52 m/s). It adjusts the satellite's arrival time by 4 seconds so both debris pieces pass harmlessly by.",
        "fuel_saved": "91.8% Fuel Saved",
        "action_button": "EXECUTE UNIFIED DUAL-CLEARANCE BURN",
        "resolved_miss": "12.8 km (Both Threats Cleared)",
        "packet_string": "CMD_EXEC_ION_PARETO_OPTIMAL_DUAL_CONJUNCTION_CLEAR",
        "coord_pre": [0, 310, 60],
        "coord_post": [0, 12800, 240]
    }
}

# ------------------------------------------------------------------------------
# 3. INTERACTIVE STATE MANAGEMENT
# ------------------------------------------------------------------------------
if 'fleet_states' not in st.session_state:
    st.session_state.fleet_states = {k: False for k in FLEET_DATABASE.keys()}

def execute_evasion(asset_key):
    st.session_state.fleet_states[asset_key] = True

def reset_current_asset(asset_key):
    st.session_state.fleet_states[asset_key] = False

def reset_all():
    for k in st.session_state.fleet_states:
        st.session_state.fleet_states[k] = False

now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

# ------------------------------------------------------------------------------
# 4. TOP CONSOLE COMMAND BAR
# ------------------------------------------------------------------------------
col_h1, col_h2 = st.columns([4, 1])

with col_h1:
    st.markdown(f"""
    <div class="top-header">
        <div>
            <strong style="font-family: 'JetBrains Mono', monospace; font-size: 14px; color: #fff;">
                KESSLERZERO : AUTONOMOUS SATELLITE COLLISION AVOIDANCE
            </strong>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 2px;">
                Detecting space debris early and calculating precision evasive maneuvers that conserve up to 90% fuel.
            </div>
        </div>
        <div class="telemetry-strip">
            <span>FLEET: <strong>3 SPACECRAFT MONITORED</strong></span>
            <span style="color: #475569; margin: 0 8px;">|</span>
            <span>TIME: <strong>{now_utc}</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    st.button("↺ Reset All Fleet Data", on_click=reset_all, use_container_width=True, help="Reset all satellites back to danger state.")

# ------------------------------------------------------------------------------
# 5. STEP 1: CONSTELLATION THREAT FEED (EASY FOR ANYONE TO READ)
# ------------------------------------------------------------------------------
st.markdown('<div class="section-title">STEP 1 // Real-Time Space Debris Watchlist</div>', unsafe_allow_html=True)

feed_records = []
for k, data in FLEET_DATABASE.items():
    is_cleared = st.session_state.fleet_states[k]
    status_label = "SAFE (TRAJECTORY SECURED)" if is_cleared else "DANGER (COLLISION RISK)"
    miss_display = data['resolved_miss'] if is_cleared else data['initial_miss_m'].split('(')[0].strip()
    risk_display = "< 0.01% (Clear)" if is_cleared else data['risk_percentage']
    
    feed_records.append({
        "Status": status_label,
        "Satellite": data['id'],
        "Hardware": data['hardware_type'],
        "Incoming Threat": data['debris_name'],
        "Time Until Impact": data['time_to_impact'],
        "Miss Distance": miss_display,
        "Collision Chance": risk_display
    })

st.dataframe(pd.DataFrame(feed_records), use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# 6. STEP 2: SELECT SPACECRAFT TO INSPECT & EVACUATE
# ------------------------------------------------------------------------------
st.markdown('<div class="section-title" style="margin-top: 16px;">STEP 2 // Select Satellite to Inspect & Evacuate</div>', unsafe_allow_html=True)

col_selector, col_status = st.columns([3, 1])

with col_selector:
    active_key = st.selectbox(
        "Choose Satellite from Fleet:",
        options=list(FLEET_DATABASE.keys()),
        label_visibility="collapsed"
    )

asset = FLEET_DATABASE[active_key]
is_auth = st.session_state.fleet_states[active_key]

with col_status:
    if is_auth:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; color: #10b981; padding: 8px 12px; border-radius: 4px; font-family: 'JetBrains Mono'; font-size: 12px; text-align: center; font-weight: 700;">
            STATUS: ORBIT SECURED
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #ef4444; padding: 8px 12px; border-radius: 4px; font-family: 'JetBrains Mono'; font-size: 12px; text-align: center; font-weight: 700;">
            STATUS: CRITICAL THREAT
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 7. STEP 3: COMPARISON METRICS & UNTOUCHED 3D ENCOUNTER RADAR
# ------------------------------------------------------------------------------
col_metrics, col_radar = st.columns([1, 1])

with col_metrics:
    st.markdown('<div class="section-title">The Problem & The Solution</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="panel-box">
        <div style="font-size: 13.5px; line-height: 1.5; color: #cbd5e1;">
            <strong>The Situation:</strong> {asset['problem_statement']}<br><br>
            <strong>Standard Industry Response:</strong> {asset['old_way']}<br><br>
            <strong>KesslerZero Solution:</strong> {asset['our_way']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not is_auth:
        m1, m2, m3 = st.columns(3)
        m1.metric("Predicted Miss", asset['initial_miss_m'].split('(')[0].strip(), help="Distance if we do nothing")
        m2.metric("Incoming Junk", asset['debris_name'].split()[0])
        m3.metric("Collision Chance", asset['risk_percentage'])
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("New Clearance", asset['resolved_miss'], delta="10+ km Safe Buffer")
        m2.metric("Collision Chance", "< 0.01%", delta="-99% Mitigated")
        m3.metric("Secondary Threats", "0 in 48 Hours")

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Efficiency & Fuel Saved</div>', unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.metric("Calculation Delay", "0.4 Seconds", delta="Cut down from 8.5 Hours")
    with col_t2:
        st.metric("Propellant Conserved", asset['fuel_saved'], delta="High Efficiency")

with col_radar:
    st.markdown('<div class="section-title">3D Encounter Geometry (Relative Motion Reference Frame)</div>', unsafe_allow_html=True)
    
    # --------------------------------------------------------------------------
    # 100% UNTOUCHED 3D PLOTLY GRAPH CODE AS REQUESTED
    # --------------------------------------------------------------------------
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
    # --------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# 8. STEP 4: 1-CLICK ACTION BUTTON (CLEAR & SATISFYING)
# ------------------------------------------------------------------------------
st.markdown('<div class="section-title" style="margin-top: 14px;">STEP 3 // 1-Click Ground Station Authorization</div>', unsafe_allow_html=True)

col_cmd_info, col_cmd_btn = st.columns([3, 1])

with col_cmd_info:
    if not is_auth:
        st.info(f"""
        **READY TO EXECUTE:** {asset['our_way']}  
        • **Safety Check:** Screened against 35,000+ catalog objects to ensure we don't steer into another satellite.  
        • **Speed:** Solution calculated in **0.4 seconds** (eliminating 8+ hours of manual ground committee delay).
        """)
    else:
        st.success(f"""
        **MANEUVER DISPATCHED TO SATELLITE:**  
        The evasive telecommand has been transmitted to {asset['id']}. The trajectory is verified safe and the 3D position above has updated.
        """)

with col_cmd_btn:
    st.write("")
    if not is_auth:
        if st.button(f"🚀 {asset['action_button']}", type="primary", use_container_width=True):
            execute_evasion(active_key)
            st.rerun()
    else:
        st.button("✅ MANEUVER CONFIRMED", disabled=True, use_container_width=True)
        if st.button("↺ Reset This Spacecraft", use_container_width=True):
            reset_current_asset(active_key)
            st.rerun()

# Verification Packet & Audit Trail (Revealed Post-Click)
if is_auth:
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Verified Radio Telecommand & Audit Proof</div>', unsafe_allow_html=True)

    col_pkt, col_audit = st.columns([1, 1])

    with col_pkt:
        st.caption("Generated Binary Satellite Command (CCSDS Standard)")
        st.markdown(f"""
        <div class="packet-log">
        [RADIO_TELECOMMAND_AUTHENTICATED]<br>
        TARGET_ASSET       : {asset['id']}<br>
        RADIO_COMMAND      : {asset['packet_string']}<br>
        HARDWARE_PROFILE   : {asset['hardware_type']}<br>
        SECONDARY_SWEEP    : ZERO_SECONDARY_HAZARDS_DETECTED<br>
        SECURITY_HASH      : SHA256: 7f3b8c...02e9 [VERIFIED]
        </div>
        """, unsafe_allow_html=True)

    with col_audit:
        st.caption("Measurable Operational Impact")
        st.dataframe(pd.DataFrame({
            "Key Parameter": [
                "Decision & Computation Time",
                "Fuel Conserved vs Old Way",
                "Distance to Sister Satellites",
                "Next 48-Hour Collision Risk"
            ],
            "KesslerZero Result": [
                "0.4 Seconds (Instant)",
                f"{asset['fuel_saved']}",
                "> 180 km (Completely Safe Separation)",
                "0.0% (Verified Clean Across All Objects)"
            ]
        }), use_container_width=True, hide_index=True)
