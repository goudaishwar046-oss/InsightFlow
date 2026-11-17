import streamlit as st
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest
from ui.components import render_page_header, require_dataset_notice
from config import THEME

render_page_header("Anomaly Detection", "Identify potential unusual values using IQR, Z-Score, or Isolation Forest")

if require_dataset_notice():
    df = st.session_state["cleaned_df"]
    num_cols = df.select_dtypes(include="number").columns.tolist()

    if not num_cols:
        st.warning("Anomaly detection requires at least one numerical column.")
    else:
        c1, c2 = st.columns([2, 2])
        with c1:
            target_col = st.selectbox("Target Numerical Column", num_cols)
        with c2:
            method = st.selectbox("Detection Method", ["IQR (Interquartile Range)", "Z-Score", "Isolation Forest (ML)"])

        series = df[target_col].dropna()
        if method.startswith("IQR"):
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            mult = st.session_state["iqr_multiplier"]
            mask = (df[target_col] < q1 - mult * iqr) | (df[target_col] > q3 + mult * iqr)
        elif method == "Z-Score":
            z_thresh = st.session_state["z_threshold"]
            z_scores = np.abs((df[target_col] - series.mean()) / (series.std() or 1))
            mask = z_scores > z_thresh
        else:
            iso = IsolationForest(contamination=0.05, random_state=42)
            clean_idx = series.index
            preds = iso.fit_predict(series.values.reshape(-1, 1))
            mask = df.index.isin(clean_idx[preds == -1])

        outliers_df = df[mask]
        severity = "High" if len(outliers_df) / max(len(df), 1) > 0.08 else ("Moderate" if len(outliers_df) > 0 else "Low")

        m1, m2, m3 = st.columns(3)
        m1.metric("Potential Outliers Flagged", f"{len(outliers_df)}")
        m2.metric("Outlier Share", f"{len(outliers_df) / max(len(df), 1) * 100:.1f}%")
        m3.metric("Severity Level", severity)

        st.info("Note: Flagged records represent **potential unusual values** for human review and are not automatically errors.")

        plot_df = df.copy()
        plot_df["Status"] = np.where(mask, "Potential Anomaly", "Normal")
        fig = px.box(
            plot_df,
            y=target_col,
            points="all",
            color="Status",
            color_discrete_map={"Normal": THEME["primary"], "Potential Anomaly": THEME["error"]},
            title=f"Outlier Inspection for {target_col}",
        )
        fig.update_layout(plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

        if not outliers_df.empty:
            st.subheader("Flagged Records")
            st.dataframe(outliers_df, use_container_width=True)
