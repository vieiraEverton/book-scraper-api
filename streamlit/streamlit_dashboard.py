import streamlit as st
import requests

API_URL = "http://localhost:8000/api/v1/stats/performance"

st.title("FastAPI Performance Dashboard")

try:
    response = requests.get(API_URL)
    data = response.json()

    st.metric("Total Requests", data["total_requests"])
    st.metric("Avg Response Time (ms)", data["average_response_time_ms"])

    st.subheader("Per Endpoint Metrics")
    for path, stats in data["per_path"].items():
        st.write(f"**{path}** — {stats['count']} requests, {stats['average_time_ms']} ms avg")

except Exception as e:
    st.error(f"Could not fetch metrics: {e}")