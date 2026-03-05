
import streamlit as st
import yfinance as yf
import math

st.set_page_config(page_title="SPX Cockpit v4", layout="wide")

st.title("SPX Trading Cockpit v4")

# --- Live market data ---
spx = yf.Ticker("^GSPC").history(period="1d", interval="1m")["Close"].iloc[-1]
vix = yf.Ticker("^VIX").history(period="1d", interval="1m")["Close"].iloc[-1]

m1, m2, m3 = st.columns(3)
m1.metric("SPX", round(spx,2))
m2.metric("VIX", round(vix,2))
gamma_regime = "POSITIVE" if vix < 25 else "VOLATILE"
m3.metric("Gamma Regime (proxy)", gamma_regime)

st.divider()

# --- Expected Move ---
daily_em = spx * vix / 16 / math.sqrt(365)
weekly_em = daily_em * math.sqrt(5)

upper = spx + weekly_em
lower = spx - weekly_em

e1, e2, e3 = st.columns(3)
e1.metric("Daily EM", round(daily_em,1))
e2.metric("Weekly EM", round(weekly_em,1))
e3.metric("Expected Range", f"{round(lower)} — {round(upper)}")

st.divider()

# --- Structure inputs (can later be automated via API) ---
st.subheader("Market Structure")

c1, c2, c3, c4 = st.columns(4)

put_wall = c1.number_input("Put Wall", value=0)
call_wall = c2.number_input("Call Wall", value=0)
gamma_node = c3.number_input("Gamma Node", value=0)
max_pain = c4.number_input("Max Pain", value=0)

oi_cluster = st.number_input("Largest OI Cluster", value=0)

st.divider()

# --- Pin Model ---
pin_level = gamma_node if gamma_node else max_pain
distance = abs(spx - pin_level) if pin_level else None

if distance is None:
    pin_prob = "N/A"
elif distance < 30:
    pin_prob = "HIGH"
elif distance < 80:
    pin_prob = "MEDIUM"
else:
    pin_prob = "LOW"

p1, p2, p3 = st.columns(3)
p1.metric("Expected Pin", pin_level if pin_level else "N/A")
p2.metric("Distance to Pin", round(distance,1) if distance else "N/A")
p3.metric("Pin Probability", pin_prob)

st.divider()

# --- Trade Signal ---
mid = (put_wall + call_wall)/2 if (put_wall and call_wall) else spx

if abs(spx-mid) < 40:
    trade_signal = "IRON CONDOR / DOUBLE BWB"
elif spx > mid:
    trade_signal = "CALL BWB"
else:
    trade_signal = "PUT BWB"

st.subheader("Trade Signal")
st.success(trade_signal)

st.divider()

# --- Suggested Structures ---
st.subheader("Suggested BWB Structures")

call_long = call_wall
call_short = call_wall + 5
call_wing = call_wall + 15

put_long = put_wall - 15
put_short = put_wall - 5
put_wing = put_wall

b1, b2 = st.columns(2)

with b1:
    st.write("CALL BWB")
    st.write(f"{call_long} / {call_short} / {call_wing}")

with b2:
    st.write("PUT BWB")
    st.write(f"{put_long} / {put_short} / {put_wing}")

st.divider()

# --- Gamma danger zone ---
danger_low = call_short - 10
danger_high = call_short + 10

st.subheader("Gamma Danger Zone")
st.warning(f"{danger_low} — {danger_high}")

st.divider()

st.info("Tip: If SPX approaches the danger zone, consider closing or hedging the BWB.")
