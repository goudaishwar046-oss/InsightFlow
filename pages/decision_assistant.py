import streamlit as st
from ui.components import render_page_header, require_dataset_notice

render_page_header("Decision Assistant", "Translate statistical findings into structured Observations, Explanations, and Recommended Actions")

if require_dataset_notice():
    df = st.session_state["cleaned_df"]
    num_cols = df.select_dtypes(include="number").columns.tolist()

    questions = [
        "What are the top data quality risks in this dataset?",
        "Are there unusual numerical spikes or drops requiring review?",
        "Which segment or category drives the highest concentration?",
        "Is this dataset ready for executive reporting?",
    ]

    selected_q = st.selectbox("Select an Analytical Question", questions)

    if st.button("Generate Decision Brief", type="primary"):
        missing_cnt = int(df.isna().sum().sum())
        dup_cnt = int(df.duplicated().sum())

        with st.container(border=True):
            st.markdown(f"### Prompt: *{selected_q}*")
            st.markdown(f"**1. Observation:** The active dataset contains **{len(df):,} rows**, **{missing_cnt} missing cells**, and **{dup_cnt} duplicate records**.")
            st.markdown(
                "**2. Possible Explanation:** Incomplete upstream data ingestion or unvalidated form submissions often introduce nulls and duplicate keys, which can skew aggregate averages."
            )
            st.markdown(
                "**3. Recommended Action:** Run deduplication and median/mode imputation in **Upload Dataset**, then verify top-end values in **Anomaly Detection** before exporting."
            )
            st.caption("Disclaimer: Rule-based observations highlight statistical patterns and do not prove causation.")
