import streamlit as st
from config import APP_NAME, APP_TAGLINE, DOMAINS
from ui.components import inject_saas_css
from ui.state import init_session_state, load_sample_dataset

st.set_page_config(
    page_title=f"{APP_NAME} – {APP_TAGLINE}",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()
inject_saas_css()

# Define all 10 required pages using st.navigation
pages = [
    st.Page("pages/dashboard.py", title="Overview", icon="🏠", default=True),
    st.Page("pages/upload_dataset.py", title="Upload Dataset", icon="📤"),
    st.Page("pages/data_quality.py", title="Data Quality", icon="🛡️"),
    st.Page("pages/change_detective.py", title="Change Detective", icon="🔍"),
    st.Page("pages/analytics.py", title="Statistical Analytics", icon="📈"),
    st.Page("pages/anomaly_detection.py", title="Anomaly Detection", icon="⚠️"),
    st.Page("pages/decision_assistant.py", title="Decision Assistant", icon="💡"),
    st.Page("pages/history_reports.py", title="History & Reports", icon="📑"),
    st.Page("pages/stock_monitor.py", title="Stock Monitor", icon="💹"),
    st.Page("pages/settings.py", title="Settings", icon="⚙️"),
]

pg = st.navigation(pages)

# Persistent Sidebar Branding & Quick Controls
with st.sidebar:
    st.markdown(f"## 📊 {APP_NAME}")
    st.caption(APP_TAGLINE)
    st.divider()

    st.session_state["selected_domain"] = st.selectbox(
        "Active Analytics Domain",
        DOMAINS,
        index=DOMAINS.index(st.session_state["selected_domain"]),
    )

    if st.session_state["raw_df"] is None:
        if st.button("⚡ Load Demo Dataset", use_container_width=True):
            load_sample_dataset()
            st.rerun()
    else:
        df_active = st.session_state["cleaned_df"]
        st.info(
            f"**Dataset:** {st.session_state['dataset_name']}\n\n"
            f"**Rows:** {len(df_active):,} | **Cols:** {len(df_active.columns)}"
        )

pg.run()
