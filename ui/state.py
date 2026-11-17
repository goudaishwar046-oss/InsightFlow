import streamlit as st
import pandas as pd
import numpy as np
from config import DEFAULT_TICKERS


def init_session_state():
    """Initialize all required session state keys cleanly."""
    defaults = {
        "dataset_name": None,
        "raw_df": None,
        "cleaned_df": None,
        "selected_domain": "General",
        "dataset_versions": {},       # version_label -> DataFrame
        "health_scores": {},          # version_label -> dict of scores
        "watchlist": list(DEFAULT_TICKERS),
        "alert_threshold_pct": 2.5,
        "weights": {
            "completeness": 0.35,
            "uniqueness": 0.25,
            "validity": 0.25,
            "consistency": 0.15,
        },
        "z_threshold": 3.0,
        "iqr_multiplier": 1.5,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def load_sample_dataset():
    """Provide an immediate realistic dataset so all UI screens can be explored right away."""
    rng = np.random.default_rng(42)
    n = 120
    categories = ["Electronics", "SaaS Licenses", "Cloud Services", "Consulting"]
    regions = ["South", "West", "North", "East"]

    df_v1 = pd.DataFrame({
        "Order_ID": [f"ORD-{1000 + i}" for i in range(n)],
        "Date": pd.date_range("2026-01-01", periods=n, freq="D").strftime("%Y-%m-%d"),
        "Category": rng.choice(categories, size=n),
        "Region": rng.choice(regions, size=n),
        "Units_Sold": rng.integers(5, 85, size=n),
        "Revenue": np.round(rng.normal(45000, 14000, size=n), 2),
        "Discount_Pct": np.round(rng.uniform(0, 25, size=n), 1),
    })

    # Introduce realistic imperfections for Data Quality & Anomaly UI demonstration
    df_v1.loc[4, "Revenue"] = np.nan
    df_v1.loc[19, "Category"] = np.nan
    df_v1.loc[50, "Revenue"] = 185000.0  # Outlier
    df_v1 = pd.concat([df_v1, df_v1.iloc[:3]], ignore_index=True)  # 3 Duplicate rows

    # Create a v2 cleaned/updated version for Change Detective demo
    df_v2 = df_v1.drop_duplicates().copy()
    df_v2["Revenue"] = df_v2["Revenue"].fillna(df_v2["Revenue"].median())
    df_v2["Category"] = df_v2["Category"].fillna(df_v2["Category"].mode().iat[0])

    extra = pd.DataFrame({
        "Order_ID": ["ORD-2001", "ORD-2002"],
        "Date": ["2026-05-05", "2026-05-06"],
        "Category": ["SaaS Licenses", "Cloud Services"],
        "Region": ["South", "West"],
        "Units_Sold": list((45, 60)),
        "Revenue": [68000.0, 79500.0],
        "Discount_Pct": [5.0, 4.0],
    })
    df_v2 = pd.concat([df_v2, extra], ignore_index=True)

    st.session_state["dataset_name"] = "q1_q2_sales_operations.csv"
    st.session_state["raw_df"] = df_v1
    st.session_state["cleaned_df"] = df_v1.copy()
    st.session_state["selected_domain"] = "Business"
    st.session_state["dataset_versions"] = {
        "v1.0 (Raw Upload)": df_v1,
        "v1.1 (Cleaned & Updated)": df_v2,
    }
