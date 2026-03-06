import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="SPX Cockpit", layout="wide")

st.title("SPX Options Cockpit")

# ---------- MARKET DATA ----------

@st.cache_data(ttl=300)
def get_market_data():

    try:

        spx_data = pd.read_csv(
            "https://stooq.com/q/d/l/?s=^spx&i=d"
        )

        vix_data = pd.read_csv(
            "https://stooq.com/q/d/l/?s=^vix&i=d"
        )

        spx = float(spx_data["Close"].iloc[-1])
        vix = float(vix_data["Close"].iloc[-1])

        return spx, vix

    except:

        return None, None


spx, vix = get_market_data()

if spx is None or vix is None:

    st.error("Market data unavailable")
    st.stop()


# ---------- MARKET ----------

m1, m2 = st.columns(2)

m1.metric("SPX", round(spx,2))
m2.metric("VIX", round(vix,2))

st.divider()


# ---------- EXPECTED MOVE ----------

daily_em = spx * vix / 16 / math.sqrt(365)
weekly_em = daily_em * math.sqrt(5)

upper = spx + weekly_em
lower = spx - weekly_em

st.markdown("### Expected Move")

st.metric("Range", f"{round(lower)} — {round(upper)}")

st.divider()


# ---------- MARKET STRUCTURE ----------

st.markdown("### Market Structure")

c1, c2, c3, c4 = st.columns(4)

put_wall = c1.number_input("Put Wall", value=0)
call_wall = c2.number_input("Call Wall", value=0)
gamma_node = c3.number_input("Gamma Node", value=0)
max_pain = c4.number_input("Max Pain", value=0)

oi_cluster = st.number_input("Largest OI Cluster", value=0)

st.divider()


# ---------- PIN MODEL ----------

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

st.markdown("### Pin Model")

p1, p2, p3 = st.columns(3)

p1.metric("Pin", pin_level if pin_level else "N/A")
p2.metric("Distance", round(distance,1) if distance else "N/A")
p3.metric("Probability", pin_prob)

st.divider()


# ---------- FRIDAY PIN MODEL ----------

if distance is None:

    pin_friday_prob = 0
    pin_bias = "UNKNOWN"

elif distance < 30:

    pin_friday_prob = 85
    pin_bias = "STRONG PIN"

elif distance < 80:

    pin_friday_prob = 60
    pin_bias = "PIN DRIFT"

else:

    pin_friday_prob = 30
    pin_bias = "TREND RISK"


st.markdown("### Friday Pin Model")

pf1, pf2, pf3 = st.columns(3)

pf1.metric("Pin Level", pin_level)
pf2.metric("Probability", f"{pin_friday_prob}%")
pf3.metric("Bias", pin_bias)

st.divider()


# ---------- TRADE DETECTOR ----------

if distance is None:

    setup = "UNKNOWN"
    recommendation = "WAIT"

elif distance < 30:

    setup = "GAMMA COMPRESSION"
    recommendation = "DOUBLE BWB"

elif distance < 80:

    setup = "PIN DRIFT"
    recommendation = "BWB"

else:

    setup = "TREND RISK"
    recommendation = "WAIT"


st.markdown("### Today Setup")

t1, t2 = st.columns(2)

t1.metric("Market", setup)
t2.metric("Recommended", recommendation)

st.divider()


# ---------- BWB BUILDER ----------

call_long = call_wall
call_short = call_wall + 5
call_wing = call_wall + 15

put_long = put_wall - 15
put_short = put_wall - 5
put_wing = put_wall

st.markdown("### Strikes")

s1, s2 = st.columns(2)

with s1:

    st.write("CALL")
    st.write(f"{call_long} / {call_short} / {call_wing}")

with s2:

    st.write("PUT")
    st.write(f"{put_long} / {put_short} / {put_wing}")

st.divider()


# ---------- PROBABILITY ENGINE ----------

call_distance = abs(call_short - spx)
put_distance = abs(spx - put_short)

call_prob = min(100, round((weekly_em / call_distance) * 50,1)) if call_distance > 0 else 100
put_prob = min(100, round((weekly_em / put_distance) * 50,1)) if put_distance > 0 else 100

st.markdown("### Probability of Touch")

p1, p2 = st.columns(2)

p1.metric("Call Side", f"{call_prob}%")
p2.metric("Put Side", f"{put_prob}%")

st.divider()


# ---------- DANGER ZONE ----------

danger_low = call_short - 10
danger_high = call_short + 10

st.markdown("### Gamma Danger Zone")

st.warning(f"{danger_low} — {danger_high}")
