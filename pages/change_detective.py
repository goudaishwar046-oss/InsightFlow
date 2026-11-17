import streamlit as st
import pandas as pd
from ui.components import render_page_header, require_dataset_notice

render_page_header("Dataset Change Detective", "Compare two dataset versions to uncover added/removed records, schema shifts, and metric deltas")

if require_dataset_notice():
    versions = st.session_state.get("dataset_versions", {})
    version_names = list(versions.keys())

    if len(version_names) < 2:
        st.info("Save at least two dataset versions in **Upload Dataset** to compare changes.")
    else:
        c1, c2, c3 = st.columns([2, 2, 2])
        with c1:
            v_prev_name = st.selectbox("Previous Version (Baseline)", version_names, index=0)
        with c2:
            v_curr_name = st.selectbox("Latest Version (Target)", version_names, index=len(version_names) - 1)

        df_prev = versions[v_prev_name]
        df_curr = versions[v_curr_name]

        common_cols = [c for c in df_prev.columns if c in df_curr.columns]
        with c3:
            id_col = st.selectbox("Unique Identifier Column (Optional)", ["None (Aggregate Mode)"] + common_cols)

        st.divider()

        # Structural Deltas
        d1, d2, d3, d4 = st.columns(4)
        row_diff = len(df_curr) - len(df_prev)
        col_diff = len(df_curr.columns) - len(df_prev.columns)
        null_prev = int(df_prev.isna().sum().sum())
        null_curr = int(df_curr.isna().sum().sum())

        d1.metric("Row Count", f"{len(df_curr):,}", delta=f"{row_diff:+d} rows")
        d2.metric("Column Count", f"{len(df_curr.columns)}", delta=f"{col_diff:+d} cols")
        d3.metric("Missing Cells", f"{null_curr:,}", delta=f"{null_curr - null_prev:+d}", delta_color="inverse")

        if id_col != "None (Aggregate Mode)" and df_prev[id_col].is_unique and df_curr[id_col].is_unique:
            prev_ids = set(df_prev[id_col])
            curr_ids = set(df_curr[id_col])
            added_ids = curr_ids - prev_ids
            removed_ids = prev_ids - curr_ids
            d4.metric("Record Changes (by ID)", f"+{len(added_ids)} / -{len(removed_ids)}", "Exact ID match")

            tab_add, tab_rem, tab_stats = st.tabs(
                [f"🟢 Added Rows ({len(added_ids)})", f"🔴 Removed Rows ({len(removed_ids)})", "📊 Numerical Shift"]
            )
            with tab_add:
                st.dataframe(df_curr[df_curr[id_col].isin(added_ids)], use_container_width=True)
            with tab_rem:
                st.dataframe(df_prev[df_prev[id_col].isin(removed_ids)], use_container_width=True)
            with tab_stats:
                num_common = [c for c in common_cols if pd.api.types.is_numeric_dtype(df_curr[c])]
                comp_rows = []
                for col in num_common:
                    m1, m2 = df_prev[col].mean(), df_curr[col].mean()
                    pct = ((m2 - m1) / m1 * 100) if m1 != 0 else 0
                    comp_rows.append({"Column": col, "Previous Mean": round(m1, 2), "Latest Mean": round(m2, 2), "Change %": f"{pct:+.2f}%"})
                st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)
        else:
            d4.metric("Comparison Mode", "Aggregate", "No unique ID selected")
            st.warning("Comparing aggregate statistics and distributions because no unique ID column was selected.")
            num_common = [c for c in common_cols if pd.api.types.is_numeric_dtype(df_curr[c])]
            comp_rows = []
            for col in num_common:
                m1, m2 = df_prev[col].mean(), df_curr[col].mean()
                pct = ((m2 - m1) / m1 * 100) if m1 != 0 else 0
                comp_rows.append({"Column": col, "Previous Mean": round(m1, 2), "Latest Mean": round(m2, 2), "Change %": f"{pct:+.2f}%"})
            st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)
