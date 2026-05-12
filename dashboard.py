##py -m streamlit run dashboard.py
import streamlit as st
import json, os, time, pickle
import pandas as pd
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# ======================================================
# PATHS
# ======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LATEST_JSON = os.path.join(BASE_DIR, "latest.json")
CSV_FILE = os.path.join(BASE_DIR, "sensor_log.csv")
MODEL_FILE = os.path.join(BASE_DIR, "crop_model.pkl")
USERS_FILE = os.path.join(BASE_DIR, "users.json")

# ======================================================
# CONFIG
# ======================================================
st.set_page_config(page_title="Smart Agriculture Dashboard", layout="wide")

# ======================================================
# AUTH SYSTEM
# ======================================================
def load_users():
    if not os.path.exists(USERS_FILE):
        return {"admin": "admin"}  # fallback user
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"admin": "admin"}

def login_ui():
    st.title("🔐 Smart Agriculture Login")
    users = load_users()

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in users and users[u] == p:
            st.session_state["logged_in"] = True
            st.session_state["user"] = u
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.get("logged_in"):
    login_ui()
    st.stop()

# ======================================================
# LOAD MODEL SAFELY
# ======================================================
@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_FILE):
        return None
    try:
        with open(MODEL_FILE, "rb") as f:
            return pickle.load(f)
    except:
        return None

model = load_model()

# ======================================================
# SAFE DATA LOADERS
# ======================================================
def read_latest():
    if not os.path.exists(LATEST_JSON):
        return None
    try:
        with open(LATEST_JSON, "r") as f:
            return json.load(f)
    except:
        return None

@st.cache_data(ttl=5)
def read_csv():
    if not os.path.exists(CSV_FILE):
        return None
    try:
        df = pd.read_csv(CSV_FILE)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        return df.dropna(subset=["timestamp"])
    except:
        return None

data = read_latest()

if not data:
    st.warning("Waiting for live sensor data...")
    st.stop()

# ======================================================
# VALUES
# ======================================================
temp = data.get("temperature")
humidity = data.get("humidity")
moisture = data.get("soil_moisture")
status = data.get("status", "Unknown")
action = data.get("action", "Unknown")
outside_temp = data.get("outside_temp")
wind = data.get("wind_speed")
city = data.get("city", "Unknown")

def safe_float(x):
    try:
        return float(x)
    except:
        return None

t = safe_float(temp)
h = safe_float(humidity)
m = safe_float(moisture)

# ======================================================
# HEADER
# ======================================================
now = datetime.now()
hour = now.hour
greet = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 17 else "Good Evening"

st.title("🌱 Smart Agriculture Dashboard")
st.caption(f"{greet}, {st.session_state['user'].title()} 👋")
st.caption(now.strftime("%d %b %Y | %I:%M:%S %p"))
st.divider()
# ======================================================
# SMART AI + LOGIC CROP RECOMMENDATION (FIXED)
# ======================================================
st.subheader("🤖 AI Crop Recommendation")

def safe_float(x):
    try:
        return float(x)
    except:
        return None

t = safe_float(temp)
h = safe_float(humidity)
m = safe_float(moisture)

pred = None   # IMPORTANT: define pred globally for rest of app

if model is None:
    st.error("ML model not loaded")

elif None in [t, h, m]:
    st.warning("Waiting for valid sensor data...")

else:
    try:
        X = [[t, h, m]]

        probs = model.predict_proba(X)[0]
        classes = model.classes_

        top_idx = np.argsort(probs)[::-1][:3]

        pred = classes[top_idx[0]]   # ✅ now pred is defined

        st.success(f"🌾 Best crop: {pred}")

        st.markdown("### Top Recommendations:")
        for i in top_idx:
            st.write(f"• {classes[i]} — {round(probs[i]*100, 1)}%")

    except Exception as e:
        st.error(f"Prediction error: {e}")

# ======================================================
# LIVE SENSOR DATA
# ======================================================
st.subheader("📡 Live Sensor Data")

c1, c2, c3 = st.columns(3)
c1.metric("🌡 Soil Temp (°C)", temp)
c2.metric("💧 Humidity (%)", humidity)
c3.metric("🌱 Moisture (%)", moisture)

st.markdown(f"**Status:** `{status}`")
st.markdown(f"**Action:** `{action}`")
st.divider()

# ======================================================
# WEATHER
# ======================================================
st.subheader("🌦 Environmental Context")

w1, w2, w3 = st.columns(3)
w1.metric("Outside Temp", outside_temp)
w2.metric("Wind Speed", wind)
w3.metric("City", city)
st.divider()

# ======================================================
# SMART ALERTS
# ======================================================
st.subheader("⚠️ Smart Alerts")

alerts = []

try:
    if float(m) < 25:
        alerts.append(("error", "Soil moisture critically low. Irrigate immediately."))
    elif float(m) < 40:
        alerts.append(("warning", "Soil moisture low. Consider irrigation."))

    if safe_float(wind) and float(wind) > 12:
        alerts.append(("warning", "High wind may reduce irrigation efficiency."))

    if not alerts:
        alerts.append(("success", "All environmental conditions look healthy."))
except:
    alerts.append(("info", "Waiting for valid data..."))

for level, msg in alerts:
    getattr(st, level)(msg)

st.divider()

# ======================================================
# TRENDS
# ======================================================
st.subheader("📈 Historical Trends")

df = read_csv()
if df is not None and len(df) > 0:
    cols = [c for c in ["soil_temp", "soil_moisture", "outside_temp"] if c in df.columns]
    if cols:
        st.line_chart(df.set_index("timestamp")[cols])
    else:
        st.info("CSV found but missing expected columns.")
else:
    st.info("No history yet.")

st.divider()

# ======================================================
# PDF REPORT
# ======================================================
def generate_pdf(data):
    path = os.path.join(BASE_DIR, "farm_report.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()
    content = [Paragraph("Smart Agriculture Report", styles["Title"]), Spacer(1, 12)]

    for k, v in data.items():
        content.append(Paragraph(f"<b>{k}:</b> {v}", styles["BodyText"]))
        content.append(Spacer(1, 6))

    doc.build(content)
    return path

st.subheader("📄 Farm Report")

report = {
    "Temperature": temp,
    "Humidity": humidity,
    "Moisture": moisture,
    "Status": status,
    "Action": action,
    "Outside Temp": outside_temp,
    "Wind": wind,
    "City": city,
    "Recommended Crop": pred if pred else "N/A"
}

if st.button("Generate PDF Report"):
    path = generate_pdf(report)
    with open(path, "rb") as f:
        st.download_button("Download Report", f, file_name="farm_report.pdf")

st.divider()

# ======================================================
# CHATBOT
# ======================================================
st.subheader("💬 Smart Farming Assistant")

if "chat" not in st.session_state:
    st.session_state.chat = []

def bot(q):
    q = q.lower()

    if "crop" in q:
        return f"Recommended crop is {pred}" if pred else "Prediction not available yet."

    if "irrigation" in q or "water" in q:
        return f"Soil moisture is {moisture}%. Action: {action}"

    if "weather" in q:
        return f"Outside temperature is {outside_temp}°C, wind speed {wind} km/h in {city}."

    if "status" in q:
        return f"Current status: {status}. Action: {action}"

    return "Ask about crop, irrigation, weather, or farm status."

user_msg = st.chat_input("Ask about your farm...")

if user_msg:
    st.session_state.chat.append(("user", user_msg))
    st.session_state.chat.append(("bot", bot(user_msg)))

for role, msg in st.session_state.chat:
    st.chat_message("user" if role == "user" else "assistant").write(msg)

# ======================================================
# FOOTER
# ======================================================
st.divider()
st.caption("Built with ❤️ by Pratishtha")

# ======================================================
# AUTO REFRESH
# ======================================================
time.sleep(2)
st.rerun()
