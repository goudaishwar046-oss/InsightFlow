import streamlit as st
from config import APP_NAME, APP_TAGLINE, THEME


def inject_saas_css():
    """Inject clean, restrained SaaS light-theme styling over native Streamlit components."""
    st.markdown(
        f"""
        <style>
        /* App background and typography */
        .stApp {{
            background-color: {THEME['bg_main']};
            color: {THEME['text_primary']};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* Sidebar styling */
        section[data-testid="stSidebar"] {{
            background-color: {THEME['bg_sidebar']};
            border-right: 1px solid {THEME['border']};
        }}

        /* Metric cards */
        div[data-testid="stMetric"] {{
            background-color: {THEME['bg_card']};
            border: 1px solid {THEME['border']};
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        }}

        /* Containers with border */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {THEME['bg_card']};
            border-radius: 12px;
            border: 1px solid {THEME['border']};
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
        }}

        /* Primary buttons */
        .stButton > button[kind="primary"] {{
            background-color: {THEME['primary']};
            border: none;
            border-radius: 8px;
            font-weight: 600;
        }}
        .stButton > button[kind="primary"]:hover {{
            background-color: #172554;
        }}

        /* Secondary buttons */
        .stButton > button[kind="secondary"] {{
            border-radius: 8px;
            border: 1px solid {THEME['border']};
            font-weight: 500;
        }}

        /* Top Header Banner */
        .insight-header {{
            background: {THEME['bg_card']};
            border: 1px solid {THEME['border']};
            border-left: 5px solid {THEME['primary']};
            border-radius: 12px;
            padding: 16px 22px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .insight-brand {{
            font-size: 1.25rem;
            font-weight: 700;
            color: {THEME['primary']};
            margin: 0;
        }}
        .insight-sub {{
            font-size: 0.85rem;
            color: {THEME['text_muted']};
            margin: 2px 0 0 0;
        }}
        .status-pill {{
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
        }}
        .pill-active {{
            background-color: {THEME['success_bg']};
            color: {THEME['success']};
            border: 1px solid #86EFAC;
        }}
        .pill-empty {{
            background-color: {THEME['warning_bg']};
            color: {THEME['warning']};
            border: 1px solid #FDE68A;
        }}
        .badge-green {{
            background-color: {THEME['success_bg']};
            color: {THEME['success']};
            padding: 3px 10px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.8rem;
        }}
        .badge-red {{
            background-color: {THEME['error_bg']};
            color: {THEME['error']};
            padding: 3px 10px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.8rem;
        }}
        .badge-amber {{
            background-color: {THEME['warning_bg']};
            color: {THEME['warning']};
            padding: 3px 10px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.8rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(page_title: str, subtitle: str = ""):
    """Consistent SaaS header across all 10 pages showing app name, page title, and dataset status."""
    dataset_name = st.session_state.get("dataset_name")
    active_df = st.session_state.get("cleaned_df")
    if active_df is None:
        active_df = st.session_state.get("raw_df")

    if dataset_name and active_df is not None:
        status_html = (
            f'<span class="status-pill pill-active">'
            f'● Active: {dataset_name} ({len(active_df):,} rows × {len(active_df.columns)} cols)'
            f"</span>"
        )
    else:
        status_html = '<span class="status-pill pill-empty">● No Dataset Loaded</span>'

    sub_text = subtitle if subtitle else APP_TAGLINE
    st.markdown(
        f"""
        <div class="insight-header">
            <div>
                <div class="insight-brand">{APP_NAME} &nbsp;|&nbsp; <span style="color:{THEME['secondary']};">{page_title}</span></div>
                <div class="insight-sub">{sub_text}</div>
            </div>
            <div>{status_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def require_dataset_notice():
    """Friendly prompt when user navigates to an analytical page before uploading data."""
    if st.session_state.get("raw_df") is None:
        st.warning("No dataset is currently loaded. Upload a CSV or load the sample dataset to begin.")
        if st.button("Load Sample Business Dataset", type="primary"):
            from ui.state import load_sample_dataset
            load_sample_dataset()
            st.rerun()
        return False
    return True
