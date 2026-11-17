import streamlit as st
import pandas as pd
import plotly.express as px
from ui.components import render_page_header, require_dataset_notice
from config import THEME

render_page_header("Statistical Analytics", "Descriptive statistics, quartile distribution, and correlation matrix")

if require_dataset_notice():
    df = st.session_state["cleaned_df"]
    num_cols = df.select_dtypes(include="number").columns.tolist()

    if not num_cols:
        st.warning("No numerical columns found in the active dataset.")
    else:
        selected_cols = st.multiselect("Select Numerical Features", num_cols, default=num_cols)

        if selected_cols:
            stats_list = []
            for col in selected_cols:
                s = df[col].dropna()
                mode_val = s.mode().iloc[0] if not s.mode().empty else None
                stats_list.append({
                    "Column": col,
                    "Mean": round(s.mean(), 2),
                    "Median": round(s.median(), 2),
                    "Mode": round(mode_val, 2) if isinstance(mode_val, (int, float)) else mode_val,
                    "Std Dev": round(s.std(), 2),
                    "Variance": round(s.var(), 2),
                    "Min": round(s.min(), 2),
                    "25% (Q1)": round(s.quantile(0.25), 2),
                    "75% (Q3)": round(s.quantile(0.75), 2),
                    "Max": round(s.max(), 2),
                })

            st.subheader("Summary Statistics Table")
            st.dataframe(pd.DataFrame(stats_list), use_container_width=True, hide_index=True)

            if len(selected_cols) >= 2:
                st.subheader("Correlation Matrix")
                corr = df[selected_cols].corr()
                fig = px.imshow(
                    corr,
                    text_auto=".2f",
                    color_continuous_scale=["#B91C1C", "#FFFFFF", THEME["primary"]],
                    zmin=-1,
                    zmax=1,
                )
                fig.update_layout(height=420)
                st.plotly_chart(fig, use_container_width=True)
