import streamlit as st
import pandas as pd
from ui.components import render_page_header

render_page_header("Upload & Clean Dataset", "Upload raw CSV files, inspect schema issues, and apply non-destructive cleaning")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
    st.session_state["dataset_name"] = uploaded_file.name
    st.session_state["raw_df"] = raw_df
    st.session_state["cleaned_df"] = raw_df.copy()
    st.session_state["dataset_versions"]["v1.0 (Raw Upload)"] = raw_df.copy()
    st.success(f"Loaded `{uploaded_file.name}` successfully.")

raw_df = st.session_state.get("raw_df")
cleaned_df = st.session_state.get("cleaned_df")

if raw_df is not None and cleaned_df is not None:
    tab_preview, tab_clean, tab_schema = st.tabs(
        ["1. Dataset Preview & Profiling", "2. Interactive Cleaning Studio", "3. Rename & Convert Types"]
    )

    with tab_preview:
        num_cols = raw_df.select_dtypes(include="number").columns.tolist()
        cat_cols = raw_df.select_dtypes(exclude="number").columns.tolist()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Raw Rows", f"{len(raw_df):,}")
        m2.metric("Raw Columns", f"{len(raw_df.columns)}")
        m3.metric("Missing Values", f"{int(raw_df.isna().sum().sum()):,}")
        m4.metric("Duplicate Rows", f"{int(raw_df.duplicated().sum()):,}")

        st.markdown("**Column Summary**")
        profile_df = pd.DataFrame({
            "Column": raw_df.columns,
            "Data Type": raw_df.dtypes.astype(str).values,
            "Kind": ["Numerical" if c in num_cols else "Categorical" for c in raw_df.columns],
            "Missing": raw_df.isna().sum().values,
            "Unique": raw_df.nunique().values,
        })
        st.dataframe(profile_df, use_container_width=True, hide_index=True)
        st.markdown("**Raw Data Preview**")
        st.dataframe(raw_df.head(15), use_container_width=True)

    with tab_clean:
        with st.container(border=True):
            st.subheader("Select Cleaning Pipeline")
            c1, c2 = st.columns(2)
            with c1:
                rm_dups = st.checkbox("Remove duplicate records", value=True)
                rm_na_rows = st.checkbox("Drop rows with any missing values", value=False)
            with c2:
                num_fill = st.selectbox("Fill numerical missing values with", ["None", "Mean", "Median"])
                cat_fill = st.selectbox("Fill categorical missing values with", ["None", "Mode"])

            version_tag = st.text_input("Save cleaned snapshot as version label", value="v1.1 (Cleaned)")

            if st.button("Apply Cleaning Rules", type="primary"):
                df_work = raw_df.copy()
                if rm_dups:
                    df_work = df_work.drop_duplicates()
                if rm_na_rows:
                    df_work = df_work.dropna()
                else:
                    if num_fill != "None":
                        for col in df_work.select_dtypes(include="number").columns:
                            fill_val = df_work[col].mean() if num_fill == "Mean" else df_work[col].median()
                            df_work[col] = df_work[col].fillna(fill_val)
                    if cat_fill == "Mode":
                        for col in df_work.select_dtypes(exclude="number").columns:
                            modes = df_work[col].mode()
                            if not modes.empty:
                                df_work[col] = df_work[col].fillna(next(iter(modes)))

                st.session_state["cleaned_df"] = df_work
                if version_tag.strip():
                    st.session_state["dataset_versions"][version_tag.strip()] = df_work.copy()
                st.success("Cleaning applied! Original raw dataset remains untouched.")
                st.rerun()

        st.subheader("Before vs. After Comparison")
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Rows (Before → After)", f"{len(cleaned_df):,}", delta=len(cleaned_df) - len(raw_df))
        b2.metric(
            "Missing Cells",
            f"{int(cleaned_df.isna().sum().sum()):,}",
            delta=int(cleaned_df.isna().sum().sum() - raw_df.isna().sum().sum()),
            delta_color="inverse",
        )
        b3.metric(
            "Duplicates",
            f"{int(cleaned_df.duplicated().sum()):,}",
            delta=int(cleaned_df.duplicated().sum() - raw_df.duplicated().sum()),
            delta_color="inverse",
        )
        b4.download_button(
            "⬇️ Download Cleaned CSV",
            data=cleaned_df.to_csv(index=False).encode("utf-8"),
            file_name=f"cleaned_{st.session_state['dataset_name'] or 'dataset.csv'}",
            mime="text/csv",
            use_container_width=True,
        )

    with tab_schema:
        with st.container(border=True):
            st.subheader("Rename Column or Cast Data Type")
            target_col = st.selectbox("Select Column", cleaned_df.columns)
            col_a, col_b = st.columns(2)
            with col_a:
                new_name = st.text_input("New Column Name", value=target_col)
            with col_b:
                target_type = st.selectbox("Convert Data Type To", ["Keep Current", "string", "float64", "int64", "datetime64[ns]"])

            if st.button("Update Column"):
                df_mod = cleaned_df.copy()
                try:
                    if target_type != "Keep Current":
                        if target_type == "datetime64[ns]":
                            df_mod[target_col] = pd.to_datetime(df_mod[target_col])
                        else:
                            df_mod[target_col] = df_mod[target_col].astype(target_type)
                    if new_name and new_name != target_col:
                        df_mod = df_mod.rename(columns={target_col: new_name})
                    st.session_state["cleaned_df"] = df_mod
                    st.success(f"Updated column `{target_col}`.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Type conversion failed: {exc}")
else:
    st.info("Upload a CSV file above, or click **Load Demo Dataset** in the sidebar to test the UI.")
