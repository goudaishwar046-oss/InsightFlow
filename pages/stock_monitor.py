import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from ui.components import render_page_header
from config import THEME

render_page_header("Stock Market Monitor", "Track historical price trends, moving averages, volume, and custom threshold alerts")

col_in, col_period, col_btn = st.columns([2, 1, 1])
with col_in:
    ticker = st.selectbox("Select or Type Watchlist Ticker", st.session_state["watchlist"])
    new_ticker = st.text_input("Add Ticker Symbol (e.g., RELIANCE.NS, TCS.NS, AAPL)", placeholder="Enter symbol...")
with col_period:
    period = st.selectbox("Lookback Period", ["1mo", "3mo", "6mo", "1y"], index=2)
with col_btn:
    st.write("")
    st.write("")
    if st.button("➕ Add to Watchlist", use_container_width=True) and new_ticker.strip():
        sym = new_ticker.strip().upper()
        if sym not in st.session_state["watchlist"]:
            st.session_state["watchlist"].append(sym)
            st.rerun()

@st.cache_data(ttl=600)
def fetch_stock(symbol: str, lookback: str):
    return yf.Ticker(symbol).history(period=lookback)

try:
    hist = fetch_stock(ticker, period)
    if hist.empty:
        st.warning(f"No historical data returned for `{ticker}`.")
    else:
        hist["MA20"] = hist["Close"].rolling(20).mean()
        hist["Daily_Pct"] = hist["Close"].pct_change() * 100

        latest_close = hist["Close"].iloc[-1]
        daily_chg = hist["Daily_Pct"].iloc[-1]
        period_high = hist["High"].max()
        period_low = hist["Low"].min()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Latest Close", f"{latest_close:,.2f}", f"{daily_chg:+.2f}%")
        m2.metric("Period High", f"{period_high:,.2f}")
        m3.metric("Period Low", f"{period_low:,.2f}")
        m4.metric("Latest Volume", f"{int(hist['Volume'].iloc[-1]):,}")

        if abs(daily_chg) >= st.session_state["alert_threshold_pct"]:
            st.warning(f"Alert: `{ticker}` moved {daily_chg:+.2f}%, exceeding your ±{st.session_state['alert_threshold_pct']}% threshold.")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Close Price", line=dict(color=THEME["primary"], width=2.5)))
        fig.add_trace(go.Scatter(x=hist.index, y=hist["MA20"], name="20-Day MA", line=dict(color=THEME["secondary"], dash="dash")))
        fig.update_layout(title=f"{ticker} Price & 20-Day Moving Average", plot_bgcolor="white", height=420)
        st.plotly_chart(fig, use_container_width=True)

        st.caption("Disclaimer: Market data availability and delays depend on Yahoo Finance (`yfinance`). Real-time quotes are not guaranteed.")
except Exception as e:
    st.error(f"Unable to fetch market data right now: {e}")
