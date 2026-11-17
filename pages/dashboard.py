import streamlit as st
import plotly.express as px
from ui.components import render_page_header, require_dataset_notice
from config import THEME

render_page_header("Overview", "Executive summary and domain-aware automatic visualizations")

if require_dataset_notice():
    df = st.session_state["cleaned_df"]
    domain = st.session_state["selected_domain"]

    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()
    missing_total = int(df.isna().sum().sum())
    dup_total = int(df.duplicated().sum())

    # Top KPI Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records", f"{len(df):,}")
    c2.metric("Features / Columns", f"{len(df.columns)}", f"{len(num_cols)} num · {len(cat_cols)} cat")
    c3.metric("Missing Cells", f"{missing_total:,}", delta_color="inverse")
    c4.metric("Duplicate Rows", f"{dup_total:,}", delta_color="inverse")

    st.subheader(f"Domain-Aware Visuals ({domain} Mode)")

    col_left, col_right = st.columns(2)
    with col_left:
        with st.container(border=True):
            if cat_cols and num_cols:
                x_col = st.selectbox("Category Dimension", cat_cols, key="ov_cat")
                y_col = st.selectbox("Numerical Metric", num_cols, key="ov_num")
                agg_df = df.groupby(x_col, as_index=False)[y_col].sum()
                fig = px.bar(
                    agg_df,
                    x=x_col,
                    y=y_col,
                    title=f"{y_col} by {x_col}",
                    color_discrete_sequence=[THEME["primary"]],
                )
                fig.update_layout(plot_bgcolor="white", margin=dict(t=40, b=20, l=20, r=20))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Upload a dataset with both categorical and numeric columns to view category breakdowns.")

    with col_right:
        with st.container(border=True):
            if num_cols:
                dist_col = st.selectbox("Distribution Column", num_cols, key="ov_dist")
                chart_type = st.radio("Chart Style", ["Histogram", "Box Plot"], horizontal=True, key="ov_style")
                if chart_type == "Histogram":
                    fig2 = px.histogram(
                        df,
                        x=dist_col,
                        nbins=25,
                        title=f"Distribution of {dist_col}",
                        color_discrete_sequence=[THEME["secondary"]],
                    )
                else:
                    fig2 = px.box(
                        df,
                        y=dist_col,
                        title=f"Spread & Quartiles of {dist_col}",
                        color_discrete_sequence=[THEME["secondary"]],
                    )
                fig2.update_layout(plot_bgcolor="white", margin=dict(t=40, b=20, l=20, r=20))
                st.plotly_chart(fig2, use_container_width=True)

    with st.expander("Preview Active Dataset (Top 10 Rows)", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)
