from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Agent Reliability Lab", layout="wide")
st.title("Agent Reliability Lab Dashboard")

report_path = Path("artifacts/reports/latest_report.json")
if not report_path.exists():
    st.warning("No report found. Run the eval suite first.")
    st.stop()

report = json.loads(report_path.read_text(encoding="utf-8"))
summary = report["summary"]
details = report["details"]

col1, col2, col3 = st.columns(3)
col1.metric("Reliability score", summary["reliability_score"])
col2.metric("Tool precision", summary["avg_tool_precision"])
col3.metric("Safety score", summary["avg_safety_score"])

df = pd.DataFrame(details)
st.subheader("Scenario results")
st.dataframe(df, use_container_width=True)

fig = px.bar(df, x="scenario_id", y="score", hover_data=["tools_used", "handoffs"])
st.plotly_chart(fig, use_container_width=True)
