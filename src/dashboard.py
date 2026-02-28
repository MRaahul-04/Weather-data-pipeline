# Run with:
# python -m streamlit run src/dashboard.py

# =================================================
# IMPORTS
# =================================================
import pandas as pd              # Data manipulation
import streamlit as st           # Streamlit UI framework
import altair as alt             # Interactive charts
from src.database import get_connection  # DB connection helper
from zoneinfo import ZoneInfo    # Timezone support (IST)

# =================================================
# PAGE CONFIG
# =================================================
# Must be the first Streamlit call
st.set_page_config(
    page_title="Weather Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================================================
# GLOBAL UI STYLING
# =================================================
# Custom CSS for dashboard look & feel
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

/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

/* Sidebar headings & labels */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p {
    color: white !important;
    font-weight: 600;
}

/* Sidebar selectbox */
section[data-testid="stSidebar"] div[data-baseweb="select"] {
    background-color: white !important;
    border-radius: 8px;
}

/* Selected city text */
section[data-testid="stSidebar"] div[data-baseweb="select"] span {
    color: #000000 !important;
    font-weight: 500;
}

/* Radio button text */
section[data-testid="stSidebar"] div[data-baseweb="radio"] span {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# =================================================
# DASHBOARD TITLE
# =================================================
st.title("🌦️ Weather Analytics Dashboard")
st.caption(
    "A modern, interactive analytics platform for real-time and historical weather insights"
)

# =================================================
# TIMEZONE HANDLING
# =================================================
# Define India Standard Time
IST = ZoneInfo("Asia/Kolkata")

def format_timestamp_ist(series: pd.Series) -> pd.Series:
    """Convert UTC timestamps to IST and readable format."""
    return (
        pd.to_datetime(series, errors="coerce", utc=True)
        .dt.tz_convert(IST)
        .dt.strftime("%d %b %Y, %I:%M %p")
    )

# =================================================
# DATA LOADER FUNCTIONS
# =================================================
def load_kpis():
    """Load high-level KPI metrics."""
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
    """Fetch list of available cities."""
    conn = get_connection()
    cities = pd.read_sql(
        "SELECT city_name FROM cities ORDER BY city_name", conn
    )
    conn.close()
    return cities["city_name"].tolist()


def load_city_weather(city):
    """Load weather data for selected city."""
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
    """Load recent alert records."""
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
# Display summary metrics at the top
kpi, alert_count = load_kpis()

k1, k2, k3, k4 = st.columns(4)
k1.metric("📦 Total Records", int(kpi["total_records"]))
k2.metric("🏙 Cities Tracked", int(kpi["cities"]))
k3.metric("🌡 Avg Temperature (°C)", kpi["avg_temp"])
k4.metric("🚨 Alerts Today", int(alert_count))

st.divider()

# =================================================
# SIDEBAR CONTROLS
# =================================================
# User controls for filtering data
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
# Load and filter data based on selections
df_city = load_city_weather(selected_city)

if df_city.empty:
    st.warning("No data available.")
    st.stop()

if time_window == "Last 24 Hours":
    df_city = df_city.tail(24)
elif time_window == "Last 7 Days":
    df_city = df_city.tail(7 * 24)

# Convert timestamps to IST
df_city["observation_time"] = format_timestamp_ist(
    df_city["observation_time"]
)

# =================================================
# TREND CHARTS
# =================================================
# Section header with highlighted city name
st.markdown(
    f"""
    <h2 style="margin-bottom: 0;">
        📈 Weather Trends —
        <span style="background: linear-gradient(135deg, #2563eb, #1e40af);
                     color: white;
                     padding: 4px 12px;
                     border-radius: 12px;
                     font-size: 0.9em;
                     font-weight: 600;">
            {selected_city}
        </span>
    </h2>
    """,
    unsafe_allow_html=True
)
st.caption("Smooth interactive trends with hover tooltips (IST timezone)")

def line_chart(df, y, label, color):
    """Reusable line chart generator."""
    return alt.Chart(df).mark_line(
        interpolate="monotone",
        strokeWidth=3,
        color=color
    ).encode(
        x=alt.X("observation_time:N", title="Time (IST)"),
        y=alt.Y(f"{y}:Q", title=label),
        tooltip=["observation_time", y]
    ).properties(height=280)

# Temperature & humidity charts
t1, t2 = st.columns(2)
with t1:
    st.altair_chart(
        line_chart(df_city, "temperature_c", "Temperature (°C)", "#ef4444"),
        width="stretch"
    )
with t2:
    st.altair_chart(
        line_chart(df_city, "humidity", "Humidity (%)", "#3b82f6"),
        width="stretch"
    )

# Wind speed & pressure charts
t3, t4 = st.columns(2)
with t3:
    st.altair_chart(
        line_chart(df_city, "wind_speed_mps", "Wind Speed (m/s)", "#10b981"),
        width="stretch"
    )
with t4:
    st.altair_chart(
        line_chart(df_city, "pressure_hpa", "Pressure (hPa)", "#8b5cf6"),
        width="stretch"
    )

st.divider()

# =================================================
# DISTRIBUTION ANALYSIS
# =================================================
# Frequency-based views
st.subheader("📊 Distribution Analysis")
st.caption("Understand spread, variability, and concentration")

d1, d2 = st.columns(2)
with d1:
    st.bar_chart(
        df_city["temperature_c"].round().value_counts().sort_index()
    )
with d2:
    st.bar_chart(
        df_city["humidity"].round().value_counts().sort_index()
    )

st.divider()

# =================================================
# ALERTS SECTION
# =================================================
# Display recent threshold breaches
st.subheader("🚨 Recent Alerts")

alerts = load_alerts()
if not alerts.empty:
    alerts["triggered_at"] = format_timestamp_ist(
        alerts["triggered_at"]
    )

    def style_alerts(row):
        """Highlight high severity alerts."""
        return [
            "background-color: #fee2e2"
            if row["alert_type"].startswith("HIGH") else ""
            for _ in row
        ]

    st.dataframe(
        alerts.style.apply(style_alerts, axis=1),
        width="stretch"
    )
else:
    st.success("No alerts triggered recently.")

st.divider()

# =================================================
# RAW DATA VIEW
# =================================================
# Expandable table for detailed inspection
with st.expander("📄 Raw Weather Data (Latest Records)", expanded=False):
    st.dataframe(
        df_city.sort_values(
            "observation_time", ascending=False
        ).head(50),
        width="stretch",
        height=400
    )