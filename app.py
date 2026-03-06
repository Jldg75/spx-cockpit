import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="SPX Cockpit", layout="wide")

st.title("SPX Options Cockpit")

# ---------- REFRESH BUTTON ----------

if st.button("🔄 Update Market Data"):
    st.cache_data.clear()

# ---------- MARKET DATA FUNCTION ----------

@st.cache_data(ttl=300)
def get_market_data():

    try:

        spx_data = pd.read_csv(
            "https://stooq.com/q/d/l/?s=^spx&i=d"
        )

        vix_data = pd.read_csv(
            "https://stooq.com/q/d/l/?s=^vix&i=d"
        )

        spx_val = float(spx_data["Close"].iloc[-1])
        vix_val = float(vix_data["Close"].iloc[-1])

        return spx_val, vix_val

    except:

        return 0, 0


# ---------- LOAD DATA ----------

spx, vix = get_market_data()

# ---------- MARKET DISPLAY ----------

col1, col2 = st.columns(2)

col1.metric("SPX", round(spx,2))
col2.metric("VIX", round(vix,2))

st.divider()

# ---------- EXPECTED MOVE ----------

daily_em = spx * vix / 16 / math.sqrt(365)
weekly_em = daily_em * math.sqrt(5)

upper = spx + weekly_em
lower = spx - weekly_em

st.subheader("Expected Move")

st.metric("Range", f"{round(lower)} — {round(upper)}")
