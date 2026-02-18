# Run with:
# python -m streamlit run src/dashboard.py

import pandas as pd
import streamlit as st
import altair as alt
from src.database import get_connection
from zoneinfo import ZoneInfo

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Weather Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================================================
# GLOBAL UI STYLING
# =================================================
st.markdown("""
<style>

/* App background */
.stApp {
    background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
}

/* KPI cards */
div[data-testid="metric-container"] {
    background: linear-gradient(145deg, #ffffff, #f1f5f9);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}

/* Section headers */
h2, h3 {
    color: #0f172a;
    margin-top: 10px;
}

/* Table headers */
thead tr th {
    background-color: #e2e8f0 !important;
    color: #0f172a !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0f172a;
}
/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

/* Sidebar headings & labels only */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p {
    color: white !important;
    font-weight: 600;
}

/* Sidebar widgets (selectbox, radio) */
section[data-testid="stSidebar"] div[data-baseweb="select"] {
    background-color: white !important;
    border-radius: 8px;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] span {
    color: #000000 !important;   /* SELECTED CITY TEXT */
    font-weight: 500;
}

/* Radio buttons text */
section[data-testid="stSidebar"] div[data-baseweb="radio"] span {
    color: white !important;
}

/* Sidebar selectbox text visibility */


</style>
""", unsafe_allow_html=True)

# =================================================
# TITLE
# =================================================
st.title("🌦️ Weather Analytics Dashboard")
st.caption("A modern, interactive analytics platform for real-time and historical weather insights")

# =================================================
# TIMEZONE HANDLING
# =================================================
IST = ZoneInfo("Asia/Kolkata")

def format_timestamp_ist(series: pd.Series) -> pd.Series:
    return (
        pd.to_datetime(series, errors="coerce", utc=True)
        .dt.tz_convert(IST)
        .dt.strftime("%d %b %Y, %I:%M %p")
    )

# =================================================
# DATA LOADERS
# =================================================
def load_kpis():
    conn = get_connection()

    kpi = pd.read_sql("""
        SELECT
            COUNT(*) AS total_records,
            COUNT(DISTINCT city_id) AS cities,
            ROUND(AVG(temperature_c), 2) AS avg_temp
        FROM weather_data
    """, conn).iloc[0]

    alerts_today = pd.read_sql("""
        SELECT COUNT(*) AS alert_count
        FROM alerts
        WHERE DATE(triggered_at) = DATE('now')
    """, conn).iloc[0]["alert_count"]

    conn.close()
    return kpi, alerts_today


def load_cities():
    conn = get_connection()
    cities = pd.read_sql("SELECT city_name FROM cities ORDER BY city_name", conn)
    conn.close()
    return cities["city_name"].tolist()


def load_city_weather(city):
    conn = get_connection()
    df = pd.read_sql("""
        SELECT
            w.observation_time,
            w.temperature_c,
            w.humidity,
            w.wind_speed_mps,
            w.pressure_hpa
        FROM weather_data w
        JOIN cities c ON w.city_id = c.city_id
        WHERE c.city_name = ?
        ORDER BY w.observation_time
    """, conn, params=(city,))
    conn.close()
    return df


def load_alerts(limit=10):
    conn = get_connection()
    df = pd.read_sql("""
        SELECT
            c.city_name,
            a.alert_type,
            a.actual_value,
            a.threshold_value,
            a.triggered_at
        FROM alerts a
        JOIN cities c ON a.city_id = c.city_id
        ORDER BY a.triggered_at DESC
        LIMIT ?
    """, conn, params=(limit,))
    conn.close()
    return df

# =================================================
# KPI SECTION
# =================================================
kpi, alert_count = load_kpis()

k1, k2, k3, k4 = st.columns(4)
k1.metric("📦 Total Records", int(kpi["total_records"]), help="Total weather observations stored")
k2.metric("🏙 Cities Tracked", int(kpi["cities"]), help="Number of monitored cities")
k3.metric("🌡 Avg Temperature (°C)", kpi["avg_temp"], help="Overall average temperature")
k4.metric("🚨 Alerts Today", int(alert_count), help="Threshold breaches today")

st.divider()

# =================================================
# SIDEBAR CONTROLS
# =================================================
st.sidebar.header("🔎 Dashboard Controls")

cities = load_cities()
selected_city = st.sidebar.selectbox("Select City", cities)

time_window = st.sidebar.radio(
    "Time Window",
    ["All Data", "Last 24 Hours", "Last 7 Days"]
)

# =================================================
# DATA PREPARATION
# =================================================
df_city = load_city_weather(selected_city)
if df_city.empty:
    st.warning("No data available.")
    st.stop()

if time_window == "Last 24 Hours":
    df_city = df_city.tail(24)
elif time_window == "Last 7 Days":
    df_city = df_city.tail(7 * 24)

df_city["observation_time"] = format_timestamp_ist(df_city["observation_time"])

# =================================================
# TREND CHARTS
# =================================================
st.markdown(
    f"""
    <h2 style="margin-bottom: 0;">
        📈 Weather Trends —
        <span style="background: linear-gradient(135deg, #2563eb, #1e40af); color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.9em; font-weight: 600; margin-left: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
            {selected_city}
        </span>
    </h2>
    """,
    unsafe_allow_html=True
)
st.caption("Smooth interactive trends with hover tooltips (IST timezone)")

def line_chart(df, y, label, color):
    return alt.Chart(df).mark_line(
        interpolate="monotone",
        strokeWidth=3,
        color=color
    ).encode(
        x=alt.X("observation_time:N", title="Time (IST)"),
        y=alt.Y(f"{y}:Q", title=label),
        tooltip=["observation_time", y]
    ).properties(height=280)

t1, t2 = st.columns(2)
with t1:
    st.altair_chart(line_chart(df_city, "temperature_c", "Temperature (°C)", "#ef4444"), width="stretch")
with t2:
    st.altair_chart(line_chart(df_city, "humidity", "Humidity (%)", "#3b82f6"), width="stretch")

t3, t4 = st.columns(2)
with t3:
    st.altair_chart(line_chart(df_city, "wind_speed_mps", "Wind Speed (m/s)", "#10b981"), width="stretch")
with t4:
    st.altair_chart(line_chart(df_city, "pressure_hpa", "Pressure (hPa)", "#8b5cf6"), width="stretch")

st.divider()

# =================================================
# DISTRIBUTION ANALYSIS
# =================================================
st.subheader("📊 Distribution Analysis")
st.caption("Understand spread, variability, and concentration")

d1, d2 = st.columns(2)
with d1:
    st.bar_chart(df_city["temperature_c"].round().value_counts().sort_index())
with d2:
    st.bar_chart(df_city["humidity"].round().value_counts().sort_index())

st.divider()

# =================================================
# ALERTS
# =================================================
st.subheader("🚨 Recent Alerts")

alerts = load_alerts()
if not alerts.empty:
    alerts["triggered_at"] = format_timestamp_ist(alerts["triggered_at"])

    def style_alerts(row):
        return ["background-color: #fee2e2" if row["alert_type"].startswith("HIGH") else "" for _ in row]

    st.dataframe(alerts.style.apply(style_alerts, axis=1), width="stretch")
else:
    st.success("No alerts triggered recently.")

st.divider()

# =================================================
# RAW DATA
# =================================================
with st.expander("📄 Raw Weather Data (Latest Records)", expanded=False):
    st.dataframe(
        df_city.sort_values("observation_time", ascending=False).head(50),
        width="stretch",
        height=400
    )
