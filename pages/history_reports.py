import io
import streamlit as st
import pandas as pd
from ui.components import render_page_header, require_dataset_notice
from core.report_generator import generate_executive_pdf

render_page_header("History & Reports", "Inspect saved dataset versions and export formatted CSV, Excel, or PDF reports")

if require_dataset_notice():
    versions = st.session_state.get("dataset_versions", {})

    st.subheader("Saved Dataset Versions")
    hist_df = pd.DataFrame([
        {
            "Version Label": k,
            "Rows": len(v),
            "Columns": len(v.columns),
            "Missing Cells": int(v.isna().sum().sum()),
            "Duplicates": int(v.duplicated().sum()),
        }
        for k, v in versions.items()
    ])
    st.dataframe(hist_df, use_container_width=True, hide_index=True)

    st.subheader("Export Analysis Package")
    version_keys = list(versions.keys())
    default_idx = len(version_keys) - 1 if version_keys else 0
    selected_version = st.selectbox("Select Version to Export", version_keys, index=default_idx)
    export_df = versions[selected_version] if version_keys else st.session_state["cleaned_df"]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.download_button(
            "📄 Download Cleaned CSV",
            data=export_df.to_csv(index=False).encode("utf-8"),
            file_name=f"cleaned_{st.session_state['dataset_name'] or 'insightflow.csv'}",
            mime="text/csv",
            use_container_width=True,
        )

    with c2:
        excel_buf = io.BytesIO()
        with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
            export_df.to_excel(writer, sheet_name="Cleaned_Data", index=False)
            export_df.describe().to_excel(writer, sheet_name="Summary_Stats")
        st.download_button(
            "📊 Download Excel Workbook (.xlsx)",
            data=excel_buf.getvalue(),
            file_name="insightflow_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with c3:
        pdf_bytes = generate_executive_pdf(
            dataset_name=f"{st.session_state['dataset_name']} ({selected_version})",
            domain=st.session_state["selected_domain"],
            df=export_df,
            weights=st.session_state["weights"],
        )
        st.download_button(
            "📑 Download Executive PDF Report",
            data=pdf_bytes,
            file_name="insightflow_executive_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
