import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# 1. Page Configuration
st.set_page_config(page_title="Ford GoBike DB UI", page_icon="🚴", layout="wide")

st.title("🚴 Ford GoBike - Database Management Interface")
st.write("Interactive interface to explore and view the Ford GoBike PostgreSQL database.")

# 2. Database Connection Setup
@st.cache_resource
def get_db_connection():
    # Update the username, password, and port according to your PostgreSQL setup
    # Format: postgresql://username:password@localhost:5432/database_name
    engine = create_engine("postgresql://postgres:ereny123@localhost:5432/ford_gobike_db")
    return engine

try:
    engine = get_db_connection()
except Exception as e:
    st.error(f"Database connection error: {e}")

# 3. Sidebar Navigation
st.sidebar.header("🔍 View Options")
view_option = st.sidebar.radio(
    "Select View Mode:",
    ("JOIN View (Full Trips)", "Table: fact_trips", "Table: dim_user", "Table: dim_station", "Table: dim_time")
)

# 4. Fetch and Display Data
if view_option == "JOIN View (Full Trips)":
    st.subheader("📊 Combined Data View (Full Trips)")
    query = """
    SELECT 
        f.trip_id,
        f.duration_sec,
        u.user_type,
        u.gender,
        u.age,
        s1.station_name AS start_station,
        s2.station_name AS end_station,
        t.day_of_week,
        t.month,
        t.year
    FROM fact_trips f
    JOIN dim_user u ON f.user_id = u.user_id
    JOIN dim_station s1 ON f.start_station_id = s1.station_id
    JOIN dim_station s2 ON f.end_station_id = s2.station_id
    JOIN dim_time t ON f.time_id = t.time_id
    ORDER BY f.trip_id;
    """
    df = pd.read_sql(query, engine)
    
    # Display Key Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Trips", len(df))
    col2.metric("Avg Duration (sec)", int(df["duration_sec"].mean()) if not df.empty else 0)
    col3.metric("Unique Start Stations", df["start_station"].nunique() if not df.empty else 0)
    
    st.dataframe(df, use_container_width=True)

else:
    # Extract table name from radio selection
    table_name = view_option.split(": ")[1]
    st.subheader(f"📋 Table View: {table_name}")
    
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql(query, engine)
    
    st.write(f"Total Rows: **{len(df)}**")
    st.dataframe(df, use_container_width=True)