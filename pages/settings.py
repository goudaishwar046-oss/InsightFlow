import streamlit as st
from ui.components import render_page_header

render_page_header("Settings", "Configure health score weights, anomaly thresholds, and stock alert sensitivity")

with st.container(border=True):
    st.subheader("Anomaly Detection Sensitivity")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state["iqr_multiplier"] = st.slider("IQR Multiplier", 1.0, 3.0, float(st.session_state["iqr_multiplier"]), 0.1)
    with c2:
        st.session_state["z_threshold"] = st.slider("Z-Score Threshold", 2.0, 4.5, float(st.session_state["z_threshold"]), 0.1)

with st.container(border=True):
    st.subheader("Stock Market Alert Threshold")
    st.session_state["alert_threshold_pct"] = st.number_input(
        "Trigger Alert When Daily Move Exceeds (%)",
        min_value=0.5,
        max_value=20.0,
        value=float(st.session_state["alert_threshold_pct"]),
        step=0.5,
    )

st.success("All settings update live across your session.")
