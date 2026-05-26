import streamlit as st
import requests
import pandas as pd
import altair as alt

st.set_page_config(page_title="F1 Intelligence Hub", layout="wide")

# --- SIDEBAR: Global Controls ---
with st.sidebar:
    st.header("⚙️ Global Settings")
    st.write("Select parameters to update all dashboards.")
    
    # 1. Select Year
    selected_year = st.selectbox("Select Year", list(range(2024, 2017, -1)))
    
    # 2. Dynamically fetch circuits for the selected year!
    try:
        sched_res = requests.get(f"http://127.0.0.1:8000/schedule/{selected_year}")
        if sched_res.status_code == 200:
            circuit_list = sched_res.json()["circuits"]
        else:
            circuit_list = ["Error loading circuits"]
    except:
        circuit_list = ["Backend Offline"]
        
    selected_circuit = st.selectbox("Select Circuit", circuit_list)
    
    # 3. Select Driver
    grid = ["VER", "HAM", "ALO", "LEC", "SAI", "NOR", "PIA", "RUS", "PER", "OCO", "BOT", "MAG", "ALB", "TSU", "STR", "ZHO", "HUL", "SAR"]
    selected_driver = st.selectbox("Select Driver", grid)
    
    st.divider()
    st.markdown("*Note: Fetching a new year/circuit combination will take ~20 seconds to download into the Data Lake.*")

# --- MAIN PAGE ---
st.title("🏁 F1 Intelligence Hub")
st.divider()

# Create the navigation tabs
tab1, tab2, tab3 = st.tabs(["⏱️ AI Pace Predictor", "📈 Grid Telemetry", "🗺️ Circuit Analytics"])

# --- TAB 1: AI Pace Predictor ---
with tab1:
    st.header("AI Pace Predictor")
    col1, col2 = st.columns(2)
    with col1:
        selected_compound = st.selectbox("Tyre Compound", ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"])
        selected_tyre_life = st.slider("Tyre Age (Laps)", 1, 50, 10)
        
        if st.button("Predict Pace"):
            payload = {"tyre_life": selected_tyre_life, "compound": selected_compound}
            response = requests.post("http://127.0.0.1:8000/predict_pace", json=payload)
            if response.status_code == 200:
                pred = response.json()["predicted_lap_time_seconds"]
                st.metric(label="Predicted Lap Time", value=f"{pred:.3f} s")
            else:
                st.error("API Error")

# --- TAB 2: Grid Telemetry ---
with tab2:
    st.header(f"Telemetry: {selected_driver} at {selected_circuit} ({selected_year})")
    
    if st.button("Fetch Telemetry Data"):
        with st.spinner("Querying Data Lake..."):
            api_url = f"http://127.0.0.1:8000/telemetry/{selected_year}/{selected_circuit}/{selected_driver}"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                df = pd.DataFrame(response.json())
                st.success("Data successfully loaded!")
                
                st.subheader("Speed Profile")
                st.line_chart(df, x='Distance', y='Speed', color="#FF1801")
                
                st.subheader("Throttle Application")
                st.area_chart(df, x='Distance', y='Throttle', color="#00D2BE")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

# --- TAB 3: Circuit Analytics ---
with tab3:
    st.header(f"Circuit Analytics: {selected_circuit} ({selected_year})")
    colA, colB = st.columns([2, 1]) 
    
    with colB:
        st.subheader("Official FIA Database")
        # Now querying the dynamic circuit info endpoint!
        info_response = requests.get(f"http://127.0.0.1:8000/circuit_info/{selected_year}/{selected_circuit}")
        if info_response.status_code == 200:
            info = info_response.json()
            st.dataframe(pd.DataFrame(list(info.items()), columns=["Metric", "Value"]), hide_index=True)
        else:
            st.warning("Could not load circuit stats.")

    with colA:
        st.subheader("GPS Track Layout")
        st.write(f"Showing track layout based on {selected_driver}'s fastest lap telemetry.")
        
        if st.button("Render Circuit Map"):
            with st.spinner("Generating map..."):
                # Dynamically fetch the track map based on the sidebar variables
                track_response = requests.get(f"http://127.0.0.1:8000/telemetry/{selected_year}/{selected_circuit}/{selected_driver}")
                
                if track_response.status_code == 200:
                    track_df = pd.DataFrame(track_response.json())
                    
                    chart = alt.Chart(track_df).mark_circle(size=10).encode(
                        x=alt.X('X:Q', axis=None), 
                        y=alt.Y('Y:Q', axis=None),
                        color=alt.Color('Speed:Q', scale=alt.Scale(scheme='redyellowblue')) 
                    ).properties(height=500)
                    
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.error("You must fetch telemetry in Tab 2 first, or the driver did not set a lap.")