import streamlit as st
import requests
import json
import os

# Set page config for a premium look
st.set_page_config(
    page_title="NYC Taxi Fare & Duration Predictor",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown("""
<style>
    /* Dark glassmorphic container style */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(255, 255, 255, 0.25);
    }
    .metric-title {
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #888;
        margin-bottom: 8px;
    }
    .metric-val {
        font-size: 32px;
        font-weight: 700;
        color: #f9d949;
    }
    .metric-unit {
        font-size: 16px;
        color: #aaa;
        font-weight: normal;
    }
    .title-container {
        padding: 20px;
        background: linear-gradient(135deg, #1f4068, #162447);
        border-radius: 16px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .title-text {
        color: #ffffff;
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
# Prioritas: Streamlit Secrets → env var → localhost (local dev)
try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Pastikan API_URL memiliki scheme (https:// atau http://)
if API_URL and not API_URL.startswith(("http://", "https://")):
    API_URL = "https://" + API_URL

# Header Section
st.markdown("""
<div class="title-container">
    <h1 class="title-text" style="margin:0;">🚕 NYC Taxi Fare & Duration Predictor</h1>
    <p style="color: #cbd5e1; margin: 10px 0 0 0; font-size:16px;">
        Compare Machine Learning (XGBoost) and Deep Learning (PyTorch MLP) taxi ride predictions in real time
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.image("https://images.unsplash.com/photo-1492664738985-f386ad69b38f?auto=format&fit=crop&q=80&w=400", use_column_width=True)
st.sidebar.header("⚙️ Configuration")
st.sidebar.markdown(f"**API Endpoint:** `{API_URL}`")

# Check backend status
try:
    health_check = requests.get(f"{API_URL}/")
    if health_check.status_code == 200:
        st.sidebar.success("● API Connected")
    else:
        st.sidebar.warning("⚠ API connected but returned error status.")
except Exception:
    st.sidebar.error("❌ Disconnected from API. Please ensure the backend is running.")

# Input Layout
st.markdown("### 📋 Input Ride Details")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("##### 📍 Location Details")
    pu_location = st.number_input("Pickup Location ID (PULocationID)", min_value=1, max_value=265, value=132, help="NYC TAXI Zone ID")
    do_location = st.number_input("Dropoff Location ID (DOLocationID)", min_value=1, max_value=265, value=230, help="NYC TAXI Zone ID")
    
    st.markdown("##### 💳 Payment & Rate Details")
    payment_type = st.selectbox("Payment Type", [1, 2, 3, 4], format_func=lambda x: {1: "Credit Card", 2: "Cash", 3: "No Charge", 4: "Dispute"}[x])
    ratecode_id = st.selectbox("Rate Code ID", [1.0, 2.0, 3.0, 4.0, 5.0, 99.0], format_func=lambda x: {1.0: "Standard rate", 2.0: "JFK", 3.0: "Newark", 4.0: "Nassau or Westchester", 5.0: "Negotiated fare", 99.0: "Group ride"}[x])

with col2:
    st.markdown("##### 🚘 Trip Profile")
    vendor_id = st.selectbox("Vendor ID", [1, 2], format_func=lambda x: f"Creative Mobile Technologies (1)" if x == 1 else f"VeriFone Inc. (2)")
    passenger_count = st.slider("Passenger Count", min_value=1, max_value=6, value=1)
    trip_distance = st.number_input("Trip Distance (miles)", min_value=0.1, max_value=100.0, value=5.4, step=0.1)
    store_and_fwd = st.selectbox("Store and Forward Flag", ["N", "Y"], help="Did the ride record hold in vehicle memory before sending?")

with col3:
    st.markdown("##### 🕒 Time & Schedule")
    pickup_hour = st.slider("Pickup Hour (24h)", min_value=0, max_value=23, value=14)
    day_of_week = st.selectbox("Day of the Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    hour_bucket = st.selectbox("Hour Bucket", ["Late Night", "Regular", "Rush Hour"], index=1)

# Predict Button
st.markdown("<br>", unsafe_allow_html=True)
predict_btn = st.button("🚀 Predict Fare & Duration", use_container_width=True)

if predict_btn:
    # Prepare payload
    payload = {
        "VendorID": vendor_id,
        "passenger_count": float(passenger_count),
        "trip_distance": float(trip_distance),
        "RatecodeID": float(ratecode_id),
        "store_and_fwd_flag": store_and_fwd,
        "PULocationID": pu_location,
        "DOLocationID": do_location,
        "payment_type": payment_type,
        "pickup_hour": pickup_hour,
        "day_of_week": day_of_week,
        "hour_bucket": hour_bucket
    }
    
    with st.spinner("Processing models predictions..."):
        try:
            response = requests.post(f"{API_URL}/predict", json=payload)
            if response.status_code == 200:
                result = response.json()
                
                # Retrieve models predictions
                ml_res = result.get("ml_model", {})
                dl_res = result.get("dl_model", {})
                
                st.markdown("### 📊 Prediction Comparison Results")
                
                col_ml, col_dl = st.columns(2)
                
                with col_ml:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">🤖 Machine Learning - {ml_res.get('name')}</div>
                        <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                            <div>
                                <p style="margin: 0; font-size: 14px; color: #888;">ESTIMATED FARE</p>
                                <p class="metric-val">${ml_res.get('predicted_total_amount'):.2f}</p>
                            </div>
                            <div>
                                <p style="margin: 0; font-size: 14px; color: #888;">ESTIMATED DURATION</p>
                                <p class="metric-val">{ml_res.get('predicted_duration_minutes'):.1f} <span class="metric-unit">mins</span></p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col_dl:
                    st.markdown(f"""
                    <div class="metric-card" style="border-color: rgba(249, 217, 73, 0.3);">
                        <div class="metric-title" style="color: #f9d949;">🧠 Deep Learning - {dl_res.get('name')}</div>
                        <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                            <div>
                                <p style="margin: 0; font-size: 14px; color: #888;">ESTIMATED FARE</p>
                                <p class="metric-val" style="color: #f9d949;">${dl_res.get('predicted_total_amount'):.2f}</p>
                            </div>
                            <div>
                                <p style="margin: 0; font-size: 14px; color: #888;">ESTIMATED DURATION</p>
                                <p class="metric-val" style="color: #f9d949;">{dl_res.get('predicted_duration_minutes'):.1f} <span class="metric-unit">mins</span></p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Show comparison visual aid
                st.info("💡 Note: XGBoost (ML) models are generally better suited for tabular feature structures, while Deep Learning models (PyTorch MLP) capture non-linear complex feature combinations after standardized transformations.")
                
            else:
                st.error(f"Error from API ({response.status_code}): {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to API server: {e}")
