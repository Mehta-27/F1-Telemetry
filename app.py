import streamlit as st
import pandas as pd
import altair as alt
import joblib
import os
import fastf1
import time
from ingest_fastf1 import F1DataIngestor
from process_data import get_fastest_lap_telemetry, save_to_feature_store

st.set_page_config(page_title="F1 INTELLIGENCE", layout="wide", page_icon=None)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-primary: #050505;
        --bg-secondary: #080808;
        --bg-tertiary: #0a0a0a;
        --surface-glass: rgba(10,10,10,0.78);
        --surface-glass-hover: rgba(18,18,18,0.88);
        --f1-red: #FF1801;
        --f1-red-soft: rgba(255,24,1,0.12);
        --f1-red-glow: rgba(255,24,1,0.25);
        --f1-blue: #0055FF;
        --f1-teal: #00D2BE;
        --f1-yellow: #FFD700;
        --text-primary: #f0f0f0;
        --text-secondary: #888888;
        --text-tertiary: #555555;
        --text-muted: #333333;
        --border-subtle: rgba(255,255,255,0.04);
        --border-glass: rgba(255,255,255,0.06);
        --border-active: rgba(255,24,1,0.35);
        --shadow-panel: 0 8px 32px rgba(0,0,0,0.6);
        --shadow-glow: 0 0 40px rgba(255,24,1,0.08);
        --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
    }

    #root, .stApp {
        background: var(--bg-primary) !important;
        font-family: var(--font-sans);
    }

    .stApp > header { display: none !important; }

    .main > .block-container {
        padding: 2rem 2.5rem !important;
        max-width: 1600px !important;
    }

    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-subtle) !important;
        min-width: 280px !important;
    }

    section[data-testid="stSidebar"] > div {
        padding: 1.5rem 1.25rem !important;
    }

    section[data-testid="stSidebar"] .sidebar-content {
        background: transparent !important;
    }

    .stSidebar [data-testid="stMarkdown"] h2 {
        font-family: var(--font-sans);
        font-weight: 800;
        font-size: 0.65rem;
        letter-spacing: 0.25em;
        color: var(--text-tertiary);
        text-transform: uppercase;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }

    .logo-section {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 1.5rem;
    }

    .logo-icon {
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        background: var(--f1-red);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 18px var(--f1-red-glow);
        flex-shrink: 0;
    }

    .logo-text {
        font-family: var(--font-sans);
        font-weight: 800;
        font-size: 0.8rem;
        letter-spacing: 0.18em;
        color: white;
        line-height: 1.2;
    }

    .logo-sub {
        font-family: var(--font-sans);
        font-size: 0.55rem;
        letter-spacing: 0.25em;
        color: var(--text-tertiary);
        text-transform: uppercase;
    }

    .stButton > button {
        font-family: var(--font-sans);
        font-weight: 700;
        font-size: 0.7rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.25,0.46,0.45,0.94);
        width: 100%;
    }

    .stButton > button[kind="primary"] {
        background: var(--f1-red) !important;
        color: white !important;
        box-shadow: 0 0 24px rgba(255,24,1,0.15);
    }

    .stButton > button[kind="primary"]:hover {
        background: #e01500 !important;
        box-shadow: 0 0 48px rgba(255,24,1,0.3);
        transform: translateY(-1px);
    }

    .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.04) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-glass) !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.08) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-glass-hover) !important;
    }

    div[data-testid="stSelectbox"] label {
        font-family: var(--font-sans);
        font-size: 0.55rem !important;
        font-weight: 600;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--text-tertiary) !important;
    }

    div[data-testid="stSelectbox"] > div {
        background: rgba(0,0,0,0.4) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 6px !important;
    }

    div[data-testid="stSelectbox"] > div:hover {
        border-color: var(--border-active) !important;
    }

    div[data-testid="stSelectbox"] select {
        font-family: var(--font-sans);
        font-size: 0.75rem !important;
        color: var(--text-primary) !important;
        background: transparent !important;
    }

    .stSlider label {
        font-family: var(--font-sans);
        font-size: 0.55rem !important;
        font-weight: 600;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--text-tertiary) !important;
    }

    div[data-testid="stSlider"] > div {
        padding: 0.5rem 0;
    }

    div[data-testid="stSlider"] div[data-baseweb="slider"] div {
        background: #1a1a1a !important;
        height: 3px !important;
    }

    div[data-testid="stSlider"] div[role="slider"] {
        background: var(--f1-red) !important;
        box-shadow: 0 0 16px rgba(255,24,1,0.4) !important;
        border: 2px solid #1a1a1a !important;
        width: 14px !important;
        height: 14px !important;
    }

    div[data-testid="stMetric"] {
        background: var(--surface-glass);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-glass);
        border-radius: 8px;
        padding: 1rem 1.25rem;
        box-shadow: var(--shadow-panel);
        transition: all 0.3s ease;
    }

    div[data-testid="stMetric"]:hover {
        background: var(--surface-glass-hover);
        border-color: var(--border-active);
    }

    div[data-testid="stMetric"] label {
        font-family: var(--font-sans);
        font-size: 0.5rem !important;
        font-weight: 600;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--text-tertiary) !important;
    }

    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-family: var(--font-mono);
        font-weight: 300;
        font-size: 1.5rem !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.03em;
    }

    div[data-testid="stTabs"] {
        margin-bottom: 1.5rem;
    }

    div[data-testid="stTabs"] button {
        font-family: var(--font-sans);
        font-weight: 700;
        font-size: 0.65rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: var(--text-tertiary) !important;
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0.5rem 0;
        margin-right: 1.5rem;
        position: relative;
        transition: color 0.3s ease;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: white !important;
    }

    div[data-testid="stTabs"] button[aria-selected="true"]::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 100%;
        height: 2px;
        background: var(--f1-red);
        box-shadow: 0 0 12px rgba(255,24,1,0.5);
        animation: border-draw 0.3s ease;
    }

    div[data-testid="stTabs"] button:hover {
        color: var(--text-secondary) !important;
    }

    @keyframes border-draw {
        from { width: 0; }
        to { width: 100%; }
    }

    .glass-card {
        background: var(--surface-glass);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-glass);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: var(--shadow-panel);
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        background: var(--surface-glass-hover);
        border-color: var(--border-active);
        box-shadow: var(--shadow-glow);
    }

    .stat-card-glow {
        background: var(--surface-glass);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-active);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        text-align: center;
        box-shadow: var(--shadow-glow);
        animation: glow-pulse 3s ease-in-out infinite;
    }

    @keyframes glow-pulse {
        0%, 100% { box-shadow: 0 0 20px rgba(255,24,1,0.08); }
        50% { box-shadow: 0 0 50px rgba(255,24,1,0.18); }
    }

    .card-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }

    .card-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.15rem 0.5rem;
        border-radius: 3px;
        font-size: 0.45rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        background: rgba(255,255,255,0.04);
        border: 1px solid var(--border-glass);
        color: var(--text-tertiary);
    }

    .card-title {
        font-family: var(--font-sans);
        font-weight: 700;
        font-size: 1.25rem;
        letter-spacing: -0.01em;
        color: white;
        margin: 0;
    }

    .card-sub {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-top: 0.15rem;
    }

    .hero-section {
        margin-bottom: 2rem;
    }

    .hero-title {
        font-family: var(--font-sans);
        font-weight: 800;
        font-size: 1.75rem;
        letter-spacing: -0.02em;
        color: white;
        margin: 0;
    }

    .hero-sub {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 0.15rem;
    }

    .prediction-value {
        font-family: var(--font-mono);
        font-weight: 300;
        font-size: 3.5rem;
        color: white;
        letter-spacing: -0.04em;
    }

    .prediction-unit {
        font-family: var(--font-mono);
        font-size: 1rem;
        color: var(--text-tertiary);
        margin-left: 0.25rem;
    }

    .degradation-bar {
        height: 4px;
        background: rgba(0,0,0,0.4);
        border-radius: 2px;
        overflow: hidden;
        max-width: 24rem;
        margin: 0.75rem auto 0;
    }

    .degradation-fill {
        height: 100%;
        background: var(--f1-red);
        border-radius: 2px;
        transition: width 1s ease-out;
    }

    .status-dot {
        display: inline-block;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #00ff88;
        animation: dot-pulse 1.5s ease-in-out infinite;
        margin-right: 0.35rem;
    }

    @keyframes dot-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    .section-divider {
        height: 1px;
        background: var(--border-subtle);
        margin: 1.5rem 0;
    }

    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #222; border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--f1-red); }

    .stAlert {
        background: var(--surface-glass) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 8px !important;
        font-family: var(--font-sans) !important;
        font-size: 0.75rem !important;
        color: var(--text-secondary) !important;
    }

    .stAlert [data-testid="stAlertContainer"] {
        background: transparent !important;
        border: none !important;
    }

    .stAlert [data-testid="stAlertContainer"] [data-testid="stMarkdown"] {
        color: var(--text-secondary) !important;
    }

    .element-container:has(> .stAlert) {
        margin: 0.5rem 0;
    }

    .stSpinner > div {
        border-color: var(--f1-red) !important;
        border-top-color: transparent !important;
    }

    .st-emotion-cache-1gulkj5 {
        border: none !important;
    }

    iframe[title="altair.chart"] {
        border-radius: 8px;
    }

    hr {
        border-color: var(--border-subtle) !important;
    }

    .sidebar-info {
        padding: 0.75rem;
        background: rgba(0,0,0,0.3);
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        font-size: 0.55rem;
        color: var(--text-tertiary);
        line-height: 1.5;
        letter-spacing: 0.05em;
        margin-top: 1rem;
    }

    .stTabContent {
        animation: fade-slide-up 0.4s cubic-bezier(0.16,1,0.3,1);
    }

    @keyframes fade-slide-up {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
"""

ingestor = F1DataIngestor()
model_path = './models/tyre_deg_model.pkl'
model = joblib.load(model_path) if os.path.exists(model_path) else None

COMPOUNDS = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]
GRID = ["VER","HAM","ALO","LEC","SAI","NOR","PIA","RUS","PER","OCO","BOT","MAG","ALB","TSU","STR","ZHO","HUL","SAR"]
YEARS = list(range(2024, 2017, -1))

def load_schedule(year):
    schedule = fastf1.get_event_schedule(year)
    races = schedule[schedule['RoundNumber'] > 0]
    return races['Location'].tolist()

def load_telemetry(year, circuit, driver):
    file_name = f"{circuit}_{year}_{driver}_fastest"
    file_path = f'./feature_store/telemetry/{file_name}.parquet'
    if os.path.exists(file_path):
        return pd.read_parquet(file_path)
    with st.spinner("Downloading session data from F1 servers..."):
        laps_df, _ = ingestor.get_race_data(year, circuit, 'R')
        if laps_df is None:
            return None
        telemetry = get_fastest_lap_telemetry(laps_df, driver)
        if telemetry is None:
            return None
        save_to_feature_store(telemetry, 'telemetry', file_name)
        return telemetry

def load_circuit_info(year, circuit):
    schedule = fastf1.get_event_schedule(year)
    event = schedule[schedule['Location'].str.contains(circuit, case=False, na=False)]
    if event.empty:
        return None
    e = event.iloc[0]
    return {
        "Event": e['EventName'],
        "Location": e['Location'],
        "Country": e['Country'],
        "Date": str(e['EventDate'].date()),
        "Format": e['EventFormat']
    }

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown("""
<div class="logo-section">
    <div class="logo-icon">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
        </svg>
    </div>
    <div>
        <div class="logo-text">F1 INTELLIGENCE</div>
        <div class="logo-sub">Command Center</div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Parameters")
    selected_year = st.selectbox("Season", YEARS)
    circuits = load_schedule(selected_year)
    selected_circuit = st.selectbox("Circuit", circuits)
    selected_driver = st.selectbox("Driver", GRID)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-info">
        <span class="status-dot"></span> System Online<br>
        First fetch downloads from F1 servers (~20s).<br>
        Subsequent loads serve from cache.
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="hero-section">
    <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.25rem;">
        <span class="card-badge">
            <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10"/>
            </svg>
            Live Session
        </span>
        <span style="font-size:0.5rem;letter-spacing:0.15em;color:var(--text-tertiary);text-transform:uppercase;font-weight:600;">
            Formula 1 World Championship
        </span>
    </div>
    <h1 class="hero-title">Telemetry Intelligence</h1>
    <p class="hero-sub">High-resolution car data, ML pace predictions, and circuit analytics</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([" Pace Predictor", " Telemetry", " Circuit Analytics"])

with tab1:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">
        <span class="card-badge">
            <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10"/>
            </svg>
            ML Engine
        </span>
        <span style="font-size:0.5rem;letter-spacing:0.15em;color:var(--text-tertiary);text-transform:uppercase;font-weight:600;">
            Random Forest Regressor
        </span>
    </div>
    <h2 style="font-family:'Inter',sans-serif;font-weight:800;font-size:1.5rem;color:white;margin:0;letter-spacing:-0.02em;">Pace Prediction</h2>
    <p style="color:var(--text-secondary);font-size:0.8rem;margin-top:0.15rem;margin-bottom:1.5rem;">
        Lap time forecast based on tyre compound degradation model
    </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        compound = st.selectbox("Compound", COMPOUNDS, key="pred_compound")
        tyre_life = st.slider("Tyre Age", 1, 50, 10, format="%d laps")
        run_pred = st.button("Execute Simulation", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if run_pred:
            if model is None:
                st.error("ML model not found. Run train_model.py first.")
            else:
                expected = model.feature_names_in_.tolist()
                data = {'TyreLife': [tyre_life]}
                for col in expected:
                    if col != 'TyreLife':
                        data[col] = [1 if col == f'Compound_{compound}' else 0]
                df = pd.DataFrame(data)[expected]
                pred = model.predict(df)[0]

                st.markdown(f"""
                <div class="stat-card-glow" style="margin-top:0.5rem;">
                    <div style="font-size:0.5rem;letter-spacing:0.25em;color:var(--text-tertiary);text-transform:uppercase;font-weight:600;margin-bottom:0.5rem;">
                        Estimated Lap Pace
                    </div>
                    <div style="display:flex;align-items:baseline;justify-content:center;gap:0.15rem;">
                        <span class="prediction-value">{pred:.3f}</span>
                        <span class="prediction-unit">s</span>
                    </div>
                    <div class="degradation-bar">
                        <div class="degradation-fill" style="width:{min((tyre_life/50)*100,100)}%"></div>
                    </div>
                    <div style="font-size:0.55rem;color:var(--text-tertiary);margin-top:0.5rem;letter-spacing:0.1em;">
                        Degradation impact &mdash; {compound} / {tyre_life} laps
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
            <span class="card-badge">Model Info</span>
        </div>
        """, unsafe_allow_html=True)
        info_data = {
            "Algorithm": "Random Forest",
            "Estimators": "100",
            "Max Depth": "5",
            "Target": "Lap Time (s)",
            "Features": "TyreLife, Compound",
            "Training Data": "Monaco 2023"
        }
        for k, v in info_data.items():
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid var(--border-subtle);font-size:0.7rem;">
                <span style="color:var(--text-tertiary);letter-spacing:0.05em;">{k}</span>
                <span style="color:var(--text-primary);font-weight:500;font-family:var(--font-mono);font-size:0.65rem;">{v}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">
        <span class="card-badge">
            <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10"/>
            </svg>
            High-Resolution
        </span>
        <span style="font-size:0.5rem;letter-spacing:0.15em;color:var(--text-tertiary);text-transform:uppercase;font-weight:600;">
            10 Hz Telemetry
        </span>
    </div>
    <h2 style="font-family:'Inter',sans-serif;font-weight:800;font-size:1.5rem;color:white;margin:0;letter-spacing:-0.02em;">Grid Telemetry</h2>
    <p style="color:var(--text-secondary);font-size:0.8rem;margin-top:0.15rem;margin-bottom:1.5rem;">
        <span style="color:var(--f1-red);font-weight:600;">{selected_driver}</span> &middot; {selected_circuit} &middot; {selected_year}
    </p>
    """, unsafe_allow_html=True)

    if st.button("Fetch Telemetry", type="primary", use_container_width=True):
        df = load_telemetry(selected_year, selected_circuit, selected_driver)
        if df is None:
            st.error(f"No telemetry found for {selected_driver} at {selected_circuit}.")
        else:
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric("Max Speed", f"{df['Speed'].max():.0f}")
            with col_b:
                st.metric("Avg Speed", f"{df['Speed'].mean():.0f}")
            with col_c:
                st.metric("Avg Throttle", f"{df['Throttle'].mean():.1f}%")
            with col_d:
                st.metric("Avg Brake", f"{df['Brake'].mean():.1f}%")

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("""
            <div class="card-header">
                <span class="card-badge">Speed Profile</span>
                <span style="font-size:0.5rem;color:var(--text-tertiary);font-family:var(--font-mono);">km/h</span>
            </div>
            """, unsafe_allow_html=True)
            speed_chart = alt.Chart(df).mark_line(
                color="#FF1801",
                strokeWidth=2
            ).encode(
                x=alt.X('Distance:Q', axis=alt.Axis(title=None, labels=False, ticks=False)),
                y=alt.Y('Speed:Q', axis=alt.Axis(title=None, labels=False, ticks=False))
            ).properties(height=200)
            st.altair_chart(speed_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("""
            <div class="card-header">
                <span class="card-badge">Throttle / Brake</span>
            </div>
            """, unsafe_allow_html=True)
            tb_df = df[['Distance', 'Throttle', 'Brake']].melt('Distance', var_name='Channel', value_name='Value')
            tb_chart = alt.Chart(tb_df).mark_area(
                opacity=0.15,
                line={'strokeWidth': 1.5}
            ).encode(
                x=alt.X('Distance:Q', axis=alt.Axis(title=None, labels=False, ticks=False)),
                y=alt.Y('Value:Q', axis=alt.Axis(title=None, labels=False, ticks=False)),
                color=alt.Color('Channel:N', scale=alt.Scale(domain=['Throttle', 'Brake'], range=['#00D2BE', '#FF1801']))
            ).properties(height=200)
            st.altair_chart(tb_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">
        <span class="card-badge">
            <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10"/>
            </svg>
            Track Analysis
        </span>
        <span style="font-size:0.5rem;letter-spacing:0.15em;color:var(--text-tertiary);text-transform:uppercase;font-weight:600;">
            {selected_driver} &middot; Fastest Lap
        </span>
    </div>
    <h2 style="font-family:'Inter',sans-serif;font-weight:800;font-size:1.5rem;color:white;margin:0;letter-spacing:-0.02em;">Circuit Analytics</h2>
    <p style="color:var(--text-secondary);font-size:0.8rem;margin-top:0.15rem;margin-bottom:1.5rem;">
        {selected_circuit} &mdash; {selected_year} Season
    </p>
    """, unsafe_allow_html=True)

    col_analytics, col_info = st.columns([2, 1])

    with col_analytics:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="card-header">
            <span class="card-badge">GPS Track Layout</span>
            <div style="display:flex;gap:0.75rem;margin-left:auto;">
                <span style="font-size:0.45rem;display:flex;align-items:center;gap:0.25rem;color:var(--text-tertiary);">
                    <span style="width:6px;height:6px;border-radius:50%;background:#0055FF;display:inline-block;"></span> Low
                </span>
                <span style="font-size:0.45rem;display:flex;align-items:center;gap:0.25rem;color:var(--text-tertiary);">
                    <span style="width:6px;height:6px;border-radius:50%;background:#00D2BE;display:inline-block;"></span> Med
                </span>
                <span style="font-size:0.45rem;display:flex;align-items:center;gap:0.25rem;color:var(--text-tertiary);">
                    <span style="width:6px;height:6px;border-radius:50%;background:#FFD700;display:inline-block;"></span> High
                </span>
                <span style="font-size:0.45rem;display:flex;align-items:center;gap:0.25rem;color:var(--text-tertiary);">
                    <span style="width:6px;height:6px;border-radius:50%;background:#FF1801;display:inline-block;"></span> Peak
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Analyze Circuit", type="primary", use_container_width=True):
            df = load_telemetry(selected_year, selected_circuit, selected_driver)
            if df is not None and 'X' in df.columns and 'Y' in df.columns:
                track_chart = alt.Chart(df).mark_circle(size=6, opacity=0.85).encode(
                    x=alt.X('X:Q', axis=alt.Axis(title=None, labels=False, ticks=False)),
                    y=alt.Y('Y:Q', axis=alt.Axis(title=None, labels=False, ticks=False)),
                    color=alt.Color('Speed:Q', scale=alt.Scale(
                        scheme='redyellowblue',
                        domain=[df['Speed'].min(), df['Speed'].max()]
                    ))
                ).properties(height=420)
                st.altair_chart(track_chart, use_container_width=True)
            else:
                st.warning("No telemetry data available for track map.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_info:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="card-header">
            <span class="card-badge">Event Data</span>
        </div>
        """, unsafe_allow_html=True)
        info = load_circuit_info(selected_year, selected_circuit)
        if info:
            for k, v in info.items():
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;padding:0.35rem 0;border-bottom:1px solid var(--border-subtle);">
                    <span style="font-size:0.55rem;letter-spacing:0.1em;color:var(--text-tertiary);text-transform:uppercase;">{k}</span>
                    <span style="font-size:0.7rem;color:var(--text-primary);font-weight:500;">{v}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="font-size:0.7rem;color:var(--text-tertiary);padding:0.5rem 0;">
                Circuit info unavailable for this selection.
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if info:
            st.markdown('<div class="glass-card" style="margin-top:0.75rem;">', unsafe_allow_html=True)
            st.markdown("""
            <div class="card-header">
                <span class="card-badge">Session Status</span>
            </div>
            <div style="display:flex;align-items:center;gap:0.5rem;padding:0.5rem 0;">
                <span class="status-dot"></span>
                <span style="font-size:0.65rem;color:var(--text-secondary);letter-spacing:0.1em;">Data Feed Active</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:1.5rem 0 0.5rem;border-top:1px solid var(--border-subtle);margin-top:2rem;">
    <span style="font-size:0.45rem;letter-spacing:0.2em;color:var(--text-muted);text-transform:uppercase;">
        F1 Intelligence Hub &mdash; Telemetry Analysis System
    </span>
</div>
""", unsafe_allow_html=True)
