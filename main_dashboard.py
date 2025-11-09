import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import pytz
from datetime import datetime
import os
import time
from dotenv import load_dotenv
import streamlit.components.v1 as components

def show_local_clock():
    clock_html = """
    <div style="text-align:center; font-family:monospace; font-size:22px;">
      <b>Your Local Time:</b>
      <span id="localTime"></span>
    </div>
    <script>
      function updateClock() {
          const now = new Date();
          const options = { hour: '2-digit', minute: '2-digit', second: '2-digit' };
          document.getElementById("localTime").innerText = now.toLocaleTimeString([], options);
      }
      setInterval(updateClock, 1000);
      updateClock();
    </script>
    """
    components.html(clock_html, height=40)

# -------------------------------
# LOAD CONFIG & KEYS
# -------------------------------
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")      
FIREBASE_URL = "https://pocs-project-68633-default-rtdb.asia-southeast1.firebasedatabase.app"
USER_ID = "UID12345"

# -------------------------------
# STREAMLIT PAGE SETUP
# -------------------------------
st.set_page_config(page_title="🌍 Global Dashboard", page_icon="💹", layout="wide")
st.title("🌍 Unified Real-Time Dashboard")

# -------------------------------
# STYLES
# -------------------------------
st.markdown("""
<style>
.delta-red { color: #ff4d4d; font-weight: 600; }
.delta-green { color: #00c853; font-weight: 600; }
.metric-compact { margin-bottom: 0.4rem; }
.clock {
    font-size: 1.4rem;
    font-weight: 600;
    color: #00FFB3;
    text-shadow: 0 0 10px #00FFB3;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🌦️ SECTION 1: WEATHER + GLOBAL TIMES + LOCAL CLOCK
# ============================================================
st.subheader("🌦️ Global Weather & Times")

cities = ["New York", "London", "New Delhi"]
timezones = {
    "New York": "America/New_York",
    "London": "Europe/London",
    "New Delhi": "Asia/Kolkata",
}

def fetch_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url, timeout=5)
        data = res.json()
        if res.status_code != 200:
            return None, None, None
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].title()
        icon = data["weather"][0]["icon"]
        return temp, desc, icon
    except Exception:
        return None, None, None

# 4 columns: 3 cities + local time
wc1, wc2, wc3, wc4 = st.columns(4)

for col, city in zip([wc1, wc2, wc3], cities):
    temp, desc, icon = fetch_weather(city)
    tz = pytz.timezone(timezones[city])
    local_time = datetime.now(tz).strftime("%I:%M:%S %p %Z")
    with col:
        st.markdown(f"**{city}**")
        st.markdown(f"<p class='clock'>🕒 {local_time}</p>", unsafe_allow_html=True)
        if temp is not None:
            st.image(f"http://openweathermap.org/img/wn/{icon}@2x.png", width=60)
            st.markdown(f"🌡️ {temp:.1f}°C — {desc}")
        else:
            st.markdown("❌ Weather unavailable")

# Local JS-based real-time clock
with wc4:
    st.markdown("**Local Device Time**")
    components.html("""
        <div style="font-size:1.4rem;font-weight:600;color:#00FFB3;">
            🕒 <span id="local-clock"></span>
        </div>
        <script>
        function updateClock() {
            const now = new Date();
            const t = now.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:true});
            document.getElementById("local-clock").textContent = t;
        }
        setInterval(updateClock, 1000);
        updateClock();
        </script>
    """, height=50)

# ============================================================
# 💹 SECTION 2: LIVE INDIAN STOCK PRICES
# ============================================================
st.markdown("---")
st.subheader("💹 Live Indian Stock Prices (Yahoo Finance)")

tickers = [f"{s}.NS" for s in ["RELIANCE", "TCS", "INFY"]]

def fetch_stock_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="1m")
        if data.empty:
            return None, None, None
        latest_price = data["Close"].iloc[-1]
        open_price = data["Open"].iloc[0]
        prev_close = ticker.history(period="2d", interval="1d")["Close"].iloc[-2]
        return latest_price, open_price, prev_close
    except Exception:
        return None, None, None

if "prices" not in st.session_state:
    st.session_state.prices = {t: [] for t in tickers}
    st.session_state.timestamps = []

for t in tickers:
    current, open_price, prev_close = fetch_stock_price(t)
    if current is None:
        continue
    st.session_state.prices[t].append(current)
    st.session_state.timestamps.append(pd.Timestamp.now())

    change = current - prev_close
    pct_change = (change / prev_close) * 100 if prev_close else 0
    delta_color_class = "delta-green" if change >= 0 else "delta-red"
    arrow = "🟢⬆️" if change > 0 else "🔴⬇️" if change < 0 else "⚪"

    st.markdown(
        f"""
        <div class="metric-compact" style="margin-bottom: 25px;">
            <b>{t}</b><br>
            <span style="font-size:1.6rem;">₹{current:.2f}</span><br>
            <span class="{delta_color_class}">{arrow} {change:+.2f} ({pct_change:+.2f}%)</span>
        </div>
        """,
        unsafe_allow_html=True
    )

if len(st.session_state.timestamps) > 1:
    min_len = min([len(st.session_state.timestamps)] + [len(st.session_state.prices[t]) for t in tickers])
    trimmed_timestamps = st.session_state.timestamps[:min_len]
    df = pd.DataFrame(index=trimmed_timestamps)
    for t in tickers:
        df[t] = st.session_state.prices[t][:min_len]
    st.line_chart(df)

# ==========================================================
# 🔐 AES vs DES Encryption / Decryption Comparison (True Timings)
# ==========================================================
import base64
import time
from Crypto.Cipher import AES, DES
from Crypto.Random import get_random_bytes

st.markdown("---")
st.markdown("## 🔐 AES vs DES Encryption & Decryption Comparison")

st.markdown("""
Type a message below and compare the real encryption and decryption performance 
of **AES (Advanced Encryption Standard)** and **DES (Data Encryption Standard)**.
""")

# --- Helper Functions ---
def pad(data, block_size):
    padding_len = block_size - len(data) % block_size
    return data + chr(padding_len) * padding_len

def unpad(data):
    padding_len = ord(data[-1])
    return data[:-padding_len]

def aes_encrypt_decrypt(plaintext):
    """Encrypts and decrypts text using AES (ECB, 128-bit key)"""
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_ECB)

    # Measure encryption time
    start = time.perf_counter()
    ciphertext = cipher.encrypt(pad(plaintext, 16).encode())
    enc_time = (time.perf_counter() - start) * 1000

    # Measure decryption time
    decipher = AES.new(key, AES.MODE_ECB)
    start = time.perf_counter()
    decrypted = unpad(decipher.decrypt(ciphertext).decode())
    dec_time = (time.perf_counter() - start) * 1000

    b64 = base64.b64encode(ciphertext).decode()
    return b64, decrypted, enc_time, dec_time

def des_encrypt_decrypt(plaintext):
    """Encrypts and decrypts text using DES (ECB, 64-bit key)"""
    key = get_random_bytes(8)
    cipher = DES.new(key, DES.MODE_ECB)

    # Measure encryption time
    start = time.perf_counter()
    ciphertext = cipher.encrypt(pad(plaintext, 8).encode())
    enc_time = (time.perf_counter() - start) * 1000

    # Measure decryption time
    decipher = DES.new(key, DES.MODE_ECB)
    start = time.perf_counter()
    decrypted = unpad(decipher.decrypt(ciphertext).decode())
    dec_time = (time.perf_counter() - start) * 1000

    b64 = base64.b64encode(ciphertext).decode()
    return b64, decrypted, enc_time, dec_time

# --- Input Box ---
user_text = st.text_area("✍️ Enter text to encrypt:", "This is a secret message!")

if st.button("Encrypt & Compare"):
    if user_text.strip() == "":
        st.warning("Please enter a message to encrypt.")
    else:
        # Run AES and DES encryptions
        aes_ct, aes_pt, aes_enc_time, aes_dec_time = aes_encrypt_decrypt(user_text)
        des_ct, des_pt, des_enc_time, des_dec_time = des_encrypt_decrypt(user_text)

        # Display results
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("AES (Advanced Encryption Standard)")
            st.write(f"**Encryption Time:** {aes_enc_time:.6f} ms")
            st.write(f"**Decryption Time:** {aes_dec_time:.6f} ms")
            st.code(aes_ct[:200] + ("..." if len(aes_ct) > 200 else ""), language="text")
            st.write(f"🔓 Decrypted Text: `{aes_pt}`")

        with col2:
            st.subheader("DES (Data Encryption Standard)")
            st.write(f"**Encryption Time:** {des_enc_time:.6f} ms")
            st.write(f"**Decryption Time:** {des_dec_time:.6f} ms")
            st.code(des_ct[:200] + ("..." if len(des_ct) > 200 else ""), language="text")
            st.write(f"🔓 Decrypted Text: `{des_pt}`")

        # --- Bar Chart Comparison ---
        st.markdown("### ⚙️ Performance Comparison")
        st.bar_chart({
            "AES (ms)": [aes_enc_time + aes_dec_time],
            "DES (ms)": [des_enc_time + des_dec_time]
        })

        total_aes = aes_enc_time + aes_dec_time
        total_des = des_enc_time + des_dec_time
        st.info(f"🔹 AES total time: {total_aes:.6f} ms | 🔸 DES total time: {total_des:.6f} ms")

        if total_aes < total_des:
            st.success("✅ AES is faster — modern and optimized with hardware support.")
        elif total_aes > total_des:
            st.warning("⚠️ DES was faster in this run — due to timing jitter or small input size.")
        else:
            st.info("Both performed equally fast in this run.")
