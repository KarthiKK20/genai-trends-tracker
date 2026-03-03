import os
import pandas as pd
import mysql.connector
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

MYSQL_CONFIG = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'database': os.getenv('MYSQL_DB')
}

def run_query(query, params=None):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

st.set_page_config(page_title="GenAI Trends", layout="wide")
st.title("🚀 GenAI Trend Tracker - LIVE DASHBOARD")

# Sidebar
st.sidebar.header("🔍 Filters")
today = datetime.now().date()
start_date = st.sidebar.date_input("From", today - timedelta(days=7))
end_date = st.sidebar.date_input("To", today)

# 1. RECENT SCRAPES (Primary table - ALWAYS works)
st.subheader("📊 Latest Scraped Data")
query_recent = """
SELECT tool_name, platform, metric_name, 
       ROUND(metric_value, 2) as value,
       DATE(retrieved_at) as scraped_date
FROM metrics_raw 
ORDER BY retrieved_at DESC 
LIMIT 50
"""
df_recent = run_query(query_recent)
st.dataframe(df_recent, use_container_width=True, height=400)

# 2. TREND SCORES (Safe query)
col1, col2 = st.columns(2)
with col1:
    st.subheader("🏆 Top Trends")
    query_trends = """
    SELECT tool_name, ROUND(trend_score, 3) as score, rank
    FROM trend_scores 
    ORDER BY trend_score DESC 
    LIMIT 20
    """
    try:
        df_trends = run_query(query_trends)
        if not df_trends.empty:
            st.dataframe(df_trends.head(10), height=300)
            st.bar_chart(df_trends.head(10).set_index('tool_name')['score'])
        else:
            st.info("⏳ No computed trends yet")
    except:
        st.info("📊 Raw data shown above")

# 3. PLATFORM BREAKDOWN
with col2:
    st.subheader("🌐 By Platform")
    query_platform = """
    SELECT platform, 
           COUNT(*) as records,
           ROUND(AVG(metric_value), 1) as avg_value,
           ROUND(MAX(metric_value), 1) as max_value
    FROM metrics_raw 
    GROUP BY platform 
    ORDER BY records DESC
    """
    df_platform = run_query(query_platform)
    st.dataframe(df_platform, height=300)

# METRICS
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", len(df_recent))
col2.metric("Platforms", len(df_platform))
col3.metric("Unique Tools", df_recent['tool_name'].nunique())

st.markdown("---")
st.caption("✅ LIVE data from GitHub, HuggingFace, StackOverflow")
st.caption("🔄 Refresh: `python demo/run_demo.py`")
