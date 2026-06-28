import streamlit as st
import requests
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

# ============================================================
# NYC TAXI ZONE LOOKUP (sumber: NYC TLC official lookup table)
# Format: LocationID → "Borough / Zone Name"
# ============================================================
NYC_ZONES = {
    1: "EWR / Newark Airport",
    2: "Queens / Jamaica Bay",
    3: "Bronx / Allerton/Pelham Gardens",
    4: "Manhattan / Alphabet City",
    5: "Staten Island / Arden Heights",
    6: "Staten Island / Arrochar-Fort Wadsworth",
    7: "Queens / Astoria",
    8: "Queens / Astoria Park",
    9: "Queens / Auburndale",
    10: "Queens / Baisley Park",
    11: "Brooklyn / Bath Beach",
    12: "Manhattan / Battery Park",
    13: "Manhattan / Battery Park City",
    14: "Brooklyn / Bay Ridge",
    15: "Queens / Bay Terrace/Fort Totten",
    16: "Queens / Bayside",
    17: "Brooklyn / Bedford",
    18: "Bronx / Bedford Park",
    19: "Queens / Bellerose",
    20: "Bronx / Belmont",
    21: "Brooklyn / Bensonhurst East",
    22: "Brooklyn / Bensonhurst West",
    23: "Staten Island / Bloomfield/Emerson Hill",
    24: "Manhattan / Bloomingdale",
    25: "Brooklyn / Boerum Hill",
    26: "Brooklyn / Borough Park",
    27: "Bronx / Bronx Park",
    28: "Bronx / Bronxdale",
    29: "Brooklyn / Brooklyn Heights",
    30: "Brooklyn / Brooklyn Navy Yard",
    31: "Brooklyn / Brownsville",
    32: "Brooklyn / Bushwick North",
    33: "Brooklyn / Bushwick South",
    34: "Queens / Cambria Heights",
    35: "Brooklyn / Canarsie",
    36: "Brooklyn / Carroll Gardens",
    37: "Manhattan / Central Harlem",
    38: "Manhattan / Central Harlem North",
    39: "Manhattan / Central Park",
    40: "Staten Island / Charleston/Tottenville",
    41: "Manhattan / Chinatown",
    42: "Bronx / City Island",
    43: "Bronx / Claremont/Bathgate",
    44: "Manhattan / Clinton East",
    45: "Brooklyn / Clinton Hill",
    46: "Manhattan / Clinton West",
    47: "Bronx / Co-Op City",
    48: "Brooklyn / Cobble Hill",
    49: "Queens / College Point",
    50: "Brooklyn / Columbia Street",
    51: "Brooklyn / Coney Island",
    52: "Queens / Corona",
    53: "Queens / Corona",
    54: "Bronx / Crotona Park",
    55: "Bronx / Crotona Park East",
    56: "Brooklyn / Crown Heights North",
    57: "Brooklyn / Crown Heights South",
    58: "Brooklyn / Cypress Hills",
    59: "Queens / Douglaston",
    60: "Brooklyn / Downtown Brooklyn/MetroTech",
    61: "Brooklyn / DUMBO/Vinegar Hill",
    62: "Brooklyn / Dyker Heights",
    63: "Manhattan / East Chelsea",
    64: "Bronx / East Concourse/Concourse Village",
    65: "Queens / East Elmhurst",
    66: "Brooklyn / East Flatbush/Farragut",
    67: "Brooklyn / East Flatbush/Remsen Village",
    68: "Manhattan / East Harlem North",
    69: "Manhattan / East Harlem South",
    70: "Brooklyn / East New York",
    71: "Brooklyn / East New York/Pennsylvania Ave",
    72: "Bronx / East Tremont",
    73: "Manhattan / East Village",
    74: "Brooklyn / East Williamsburg",
    75: "Bronx / Eastchester",
    76: "Queens / Elmhurst",
    77: "Queens / Elmhurst/Maspeth",
    78: "Staten Island / Eltingville/Annadale",
    79: "Brooklyn / Erasmus",
    80: "Queens / Far Rockaway",
    81: "Manhattan / Financial District North",
    82: "Manhattan / Financial District South",
    83: "Brooklyn / Flatbush/Ditmas Park",
    84: "Brooklyn / Flatlands",
    85: "Queens / Flushing",
    86: "Queens / Flushing Meadows-Corona Park",
    87: "Bronx / Fordham South",
    88: "Queens / Forest Hills",
    89: "Queens / Forest Park/Highland Park",
    90: "Brooklyn / Fort Greene",
    91: "Queens / Fresh Meadows",
    92: "Staten Island / Freshkills Park",
    93: "Manhattan / Garment District",
    94: "Queens / Glen Oaks",
    95: "Queens / Glendale",
    96: "Manhattan / Governor's Island/Ellis Island",
    97: "Manhattan / Governor's Island/Liberty Island",
    98: "Manhattan / Governor's Island/NL",
    99: "Brooklyn / Gravesend",
    100: "Staten Island / Great Kills",
    101: "Staten Island / Great Kills Park",
    102: "Brooklyn / Green-Wood Cemetery",
    103: "Brooklyn / Greenpoint",
    104: "Manhattan / Greenwich Village North",
    105: "Manhattan / Greenwich Village South",
    106: "Staten Island / Grymes Hill/Clifton",
    107: "Manhattan / Hamilton Heights",
    108: "Queens / Hammels/Arverne",
    109: "Staten Island / Heartland Village/Graniteville",
    110: "Bronx / Highbridge",
    111: "Manhattan / Hell's Kitchen North",
    112: "Manhattan / Hell's Kitchen South",
    113: "Bronx / Highbridge Park",
    114: "Queens / Hillcrest/Pomonok",
    115: "Queens / Hollis",
    116: "Brooklyn / Homecrest",
    117: "Queens / Howard Beach",
    118: "Manhattan / Hudson Sq",
    119: "Bronx / Hunts Point",
    120: "Queens / Jackson Heights",
    121: "Queens / Jamaica",
    122: "Queens / Jamaica Estates",
    123: "Queens / JFK Airport",
    124: "Brooklyn / Kensington",
    125: "Queens / Kew Gardens",
    126: "Queens / Kew Gardens Hills",
    127: "Bronx / Kingsbridge Heights",
    128: "Manhattan / Kips Bay",
    129: "Queens / LaGuardia Airport",
    130: "Queens / Laurelton",
    131: "Manhattan / Lenox Hill East",
    132: "Manhattan / Lenox Hill West",
    133: "Manhattan / Lincoln Square East",
    134: "Manhattan / Lincoln Square West",
    135: "Manhattan / Little Italy/NoLiTa",
    136: "Queens / Long Island City/Hunters Point",
    137: "Queens / Long Island City/Queens Plaza",
    138: "Manhattan / Meatpacking/West Village West",
    139: "Bronx / Melrose South",
    140: "Queens / Middle Village",
    141: "Manhattan / Midtown Center",
    142: "Manhattan / Midtown East",
    143: "Manhattan / Midtown North",
    144: "Manhattan / Midtown South",
    145: "Brooklyn / Mill Basin",
    146: "Staten Island / Miller Field",
    147: "Manhattan / Morningside Heights",
    148: "Bronx / Morrisania/Melrose",
    149: "Bronx / Mott Haven/Port Morris",
    150: "Bronx / Mount Hope",
    151: "Manhattan / Murray Hill",
    152: "Queens / Murray Hill-Queens",
    153: "Staten Island / New Dorp/Midland Beach",
    154: "Queens / North Corona",
    155: "Bronx / Norwood",
    156: "Queens / Oakland Gardens",
    157: "Staten Island / Oakwood",
    158: "Manhattan / Old Astoria",
    159: "Queens / Old Astoria",
    160: "Queens / Ozone Park",
    161: "Manhattan / Park Avenue",
    162: "Manhattan / Penn Station/Madison Sq West",
    163: "Queens / Parkchester",
    164: "Bronx / Pelham Bay",
    165: "Bronx / Pelham Bay Park",
    166: "Bronx / Pelham Parkway",
    167: "Manhattan / Perishing Square North",
    168: "Queens / Pomonok/Flushing Creek",
    169: "Queens / Port Richmond",
    170: "Brooklyn / Prospect-Lefferts Gardens",
    171: "Brooklyn / Prospect Heights",
    172: "Brooklyn / Prospect Park",
    173: "Queens / Queens Village",
    174: "Queens / Queensboro Hill",
    175: "Queens / Queensbridge/Ravenswood",
    176: "Manhattan / Randalls Island",
    177: "Brooklyn / Red Hook",
    178: "Queens / Rego Park",
    179: "Queens / Richmond Hill",
    180: "Queens / Ridgewood",
    181: "Bronx / Rikers Island",
    182: "Bronx / Riverdale/North Riverdale/Fieldston",
    183: "Queens / Rockaway Park",
    184: "Queens / Roosevelt Island",
    185: "Queens / Rosedale",
    186: "Staten Island / Rossville/Woodrow",
    187: "Queens / Saint Albans",
    188: "Staten Island / Saint George/New Brighton",
    189: "Queens / Saint Michaels Cemetery/Woodside",
    190: "Queens / Santorini",
    191: "Brooklyn / Seagate/Coney Island",
    192: "Queens / Sholom Aleichem Library/Far Rockaway",
    193: "Queens / South Beach/Dongan Hills",
    194: "Staten Island / South Beach/Dongan Hills",
    195: "Queens / South Jamaica",
    196: "Queens / South Ozone Park",
    197: "Staten Island / South Williamsburg",
    198: "Brooklyn / South Williamsburg",
    199: "Queens / Springfield Gardens North",
    200: "Queens / Springfield Gardens South",
    201: "Staten Island / Stapleton/Rosebank",
    202: "Brooklyn / Starrett City",
    203: "Queens / Steinway",
    204: "Manhattan / Stuy Town/Peter Cooper Village",
    205: "Brooklyn / Stuyvesant Heights",
    206: "Manhattan / Sutton Place/Turtle Bay North",
    207: "Manhattan / Times Sq/Theatre District",
    208: "Manhattan / TriBeCa/Civic Center",
    209: "Manhattan / Two Bridges/Seward Park",
    210: "Manhattan / UN/Turtle Bay South",
    211: "Manhattan / Union Sq",
    212: "Bronx / University Heights/Morris Heights",
    213: "Manhattan / Upper East Side North",
    214: "Manhattan / Upper East Side South",
    215: "Manhattan / Upper West Side North",
    216: "Manhattan / Upper West Side South",
    217: "Bronx / Van Cortlandt Park",
    218: "Bronx / Van Cortlandt Village",
    219: "Bronx / Van Nest/Morris Park",
    220: "Manhattan / Washington Heights North",
    221: "Manhattan / Washington Heights South",
    222: "Staten Island / West Brighton",
    223: "Manhattan / West Chelsea/Hudson Yards",
    224: "Bronx / West Concourse",
    225: "Bronx / West Farms/Bronx River",
    226: "Manhattan / West Village",
    227: "Bronx / Westchester Village/Unionport",
    228: "Staten Island / Westerleigh",
    229: "Queens / Whitestone",
    230: "Queens / Willets Point",
    231: "Bronx / Williamsbridge/Baychester",
    232: "Brooklyn / Williamsburg (North Side)",
    233: "Brooklyn / Williamsburg (South Side)",
    234: "Brooklyn / Windsor Terrace",
    235: "Queens / Woodhaven",
    236: "Bronx / Woodlawn/Wakefield",
    237: "Queens / Woodside",
    238: "Manhattan / World Trade Center",
    239: "Manhattan / Yorkville East",
    240: "Manhattan / Yorkville West",
    241: "Brooklyn / Canarsie",
    242: "Brooklyn / Park Slope",
    243: "Staten Island / Todt Hill/Emerson Hill",
    244: "Staten Island / Tottenville/Great Kills",
    245: "Queens / Breezy Point/Fort Tilden/Riis Beach",
    246: "Queens / Broad Channel",
    247: "Queens / Edgemere/Far Rockaway",
    248: "Queens / Lindenwood/Howard Beach",
    249: "Queens / Rockaway Beach/Arverne",
    250: "Queens / Sommerville/Lincoln Square",
    251: "Manhattan / SoHo",
    252: "Manhattan / Manhattanville",
    253: "Queens / South Richmond Hill",
    254: "Staten Island / Silver Lake",
    255: "Brooklyn / Dyker Heights",
    256: "Staten Island / Port Ivory/Castleton",
    257: "Brooklyn / Sunset Park East",
    258: "Brooklyn / Sunset Park West",
    259: "Manhattan / Inwood",
    260: "Bronx / Marble Hill/Inwood",
    261: "Manhattan / World Trade Center",
    262: "Queens / Woodside",
    263: "Queens / Corona",
    264: "Unknown / N/A",
    265: "Unknown / N/A",
}

# Buat daftar tampilan: "ID - Borough / Zone"
def zone_display(loc_id):
    return f"{loc_id} — {NYC_ZONES.get(loc_id, 'Unknown')}"

ZONE_OPTIONS = sorted(NYC_ZONES.keys())
ZONE_DISPLAY_LIST = [zone_display(i) for i in ZONE_OPTIONS]
ZONE_DISPLAY_TO_ID = {zone_display(i): i for i in ZONE_OPTIONS}

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

    # Default index untuk Lenox Hill West (132) dan Willets Point (230)
    default_pu_idx = ZONE_OPTIONS.index(132)
    default_do_idx = ZONE_OPTIONS.index(230)

    pu_display = st.selectbox(
        "🟢 Pickup Location",
        options=ZONE_DISPLAY_LIST,
        index=default_pu_idx,
        help="Pilih zona penjemputan taxi NYC"
    )
    do_display = st.selectbox(
        "🔴 Dropoff Location",
        options=ZONE_DISPLAY_LIST,
        index=default_do_idx,
        help="Pilih zona tujuan taxi NYC"
    )

    # Konversi nama kembali ke ID untuk dikirim ke API
    pu_location = ZONE_DISPLAY_TO_ID[pu_display]
    do_location = ZONE_DISPLAY_TO_ID[do_display]

    # Tampilkan badge zona yang dipilih
    st.caption(f"📍 Pickup ID: **{pu_location}** | 🏁 Dropoff ID: **{do_location}**")

    st.markdown("##### 💳 Payment & Rate Details")
    payment_type = st.selectbox("Payment Type", [1, 2, 3, 4], format_func=lambda x: {1: "Credit Card", 2: "Cash", 3: "No Charge", 4: "Dispute"}[x])
    ratecode_id = st.selectbox("Rate Code ID", [1.0, 2.0, 3.0, 4.0, 5.0, 99.0], format_func=lambda x: {1.0: "Standard rate", 2.0: "JFK", 3.0: "Newark", 4.0: "Nassau or Westchester", 5.0: "Negotiated fare", 99.0: "Group ride"}[x])

with col2:
    st.markdown("##### 🚘 Trip Profile")
    vendor_id = st.selectbox("Vendor ID", [1, 2], format_func=lambda x: "Creative Mobile Technologies (1)" if x == 1 else "VeriFone Inc. (2)")
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

                # Tampilkan info rute
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.04); border-radius:10px; padding:12px 20px; margin-bottom:16px; border:1px solid rgba(255,255,255,0.08);">
                    <span style="color:#94a3b8; font-size:13px;">ROUTE</span><br>
                    <span style="font-size:15px;">🟢 <b>{NYC_ZONES.get(pu_location, pu_location)}</b> &nbsp;→&nbsp; 🔴 <b>{NYC_ZONES.get(do_location, do_location)}</b></span>
                </div>
                """, unsafe_allow_html=True)

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
