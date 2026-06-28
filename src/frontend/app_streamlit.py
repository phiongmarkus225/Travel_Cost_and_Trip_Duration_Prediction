import streamlit as st
import requests
import os
import math

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
    .dist-info {
        background: rgba(249, 217, 73, 0.07);
        border: 1px solid rgba(249, 217, 73, 0.25);
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 12px;
        color: #f9d949;
        margin-top: 4px;
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
    158: "Queens / Old Astoria",
    159: "Queens / Old Astoria",
    160: "Queens / Ozone Park",
    161: "Manhattan / Park Avenue",
    162: "Manhattan / Penn Station/Madison Sq West",
    163: "Bronx / Parkchester",
    164: "Bronx / Pelham Bay",
    165: "Bronx / Pelham Bay Park",
    166: "Bronx / Pelham Parkway",
    167: "Manhattan / Perishing Square North",
    168: "Queens / Pomonok/Flushing Creek",
    169: "Staten Island / Port Richmond",
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
    190: "Queens / Steinway",
    191: "Brooklyn / Seagate/Coney Island",
    192: "Queens / Far Rockaway/Edgemere",
    193: "Staten Island / South Beach/Dongan Hills",
    194: "Staten Island / South Beach/Dongan Hills",
    195: "Queens / South Jamaica",
    196: "Queens / South Ozone Park",
    197: "Brooklyn / South Williamsburg",
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
    255: "Brooklyn / Sunset Park East",
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

# ============================================================
# CENTROID KOORDINAT PER ZONA (lat, lon)
# Sumber: diturunkan dari NYC TLC Taxi Zone shapefile
# Digunakan untuk estimasi jarak antar zona
# ============================================================
ZONE_COORDS = {
    1:  (40.6895, -74.1745), 2:  (40.6089, -73.8223), 3:  (40.8657, -73.8674),
    4:  (40.7243, -73.9801), 5:  (40.5535, -74.1848), 6:  (40.6018, -74.0742),
    7:  (40.7721, -73.9301), 8:  (40.7803, -73.9321), 9:  (40.7503, -73.7951),
    10: (40.6818, -73.7896), 11: (40.6007, -74.0040), 12: (40.7033, -74.0170),
    13: (40.7118, -74.0155), 14: (40.6359, -74.0209), 15: (40.7918, -73.7912),
    16: (40.7632, -73.7751), 17: (40.6862, -73.9439), 18: (40.8701, -73.8879),
    19: (40.7182, -73.7221), 20: (40.8534, -73.8907), 21: (40.6074, -73.9934),
    22: (40.6051, -74.0126), 23: (40.6118, -74.0932), 24: (40.7867, -73.9801),
    25: (40.6862, -73.9873), 26: (40.6312, -73.9934), 27: (40.8578, -73.8721),
    28: (40.8451, -73.8618), 29: (40.6962, -73.9953), 30: (40.7004, -73.9726),
    31: (40.6629, -73.9129), 32: (40.7034, -73.9262), 33: (40.6907, -73.9240),
    34: (40.6968, -73.7354), 35: (40.6379, -73.9073), 36: (40.6801, -73.9996),
    37: (40.8118, -73.9507), 38: (40.8234, -73.9451), 39: (40.7828, -73.9654),
    40: (40.5101, -74.2348), 41: (40.7151, -73.9979), 42: (40.8504, -73.7879),
    43: (40.8401, -73.9065), 44: (40.7634, -73.9934), 45: (40.6940, -73.9651),
    46: (40.7618, -74.0001), 47: (40.8740, -73.8290), 48: (40.6868, -73.9961),
    49: (40.7879, -73.8465), 50: (40.6757, -73.9985), 51: (40.5740, -73.9818),
    52: (40.7468, -73.8618), 53: (40.7418, -73.8651), 54: (40.8368, -73.9001),
    55: (40.8318, -73.8940), 56: (40.6740, -73.9462), 57: (40.6640, -73.9451),
    58: (40.6762, -73.8871), 59: (40.7693, -73.7421), 60: (40.6921, -73.9865),
    61: (40.7034, -73.9882), 62: (40.6218, -74.0115), 63: (40.7468, -74.0001),
    64: (40.8301, -73.9185), 65: (40.7668, -73.8740), 66: (40.6473, -73.9440),
    67: (40.6373, -73.9362), 68: (40.7979, -73.9388), 69: (40.7901, -73.9426),
    70: (40.6654, -73.8851), 71: (40.6568, -73.8812), 72: (40.8451, -73.8901),
    73: (40.7265, -73.9815), 74: (40.7104, -73.9273), 75: (40.8818, -73.8318),
    76: (40.7373, -73.8765), 77: (40.7279, -73.8829), 78: (40.5412, -74.1651),
    79: (40.6512, -73.9534), 80: (40.6073, -73.7554), 81: (40.7101, -74.0101),
    82: (40.7062, -74.0140), 83: (40.6440, -73.9618), 84: (40.6262, -73.9326),
    85: (40.7671, -73.8329), 86: (40.7401, -73.8465), 87: (40.8601, -73.8979),
    88: (40.7187, -73.8490), 89: (40.6962, -73.8668), 90: (40.6940, -73.9745),
    91: (40.7334, -73.7940), 92: (40.5812, -74.1779), 93: (40.7534, -73.9940),
    94: (40.7479, -73.7101), 95: (40.7051, -73.8601), 96: (40.6912, -74.0234),
    97: (40.6979, -74.0445), 98: (40.6846, -74.0417), 99: (40.5968, -73.9784),
    100: (40.5562, -74.1512), 101: (40.5490, -74.1290), 102: (40.6551, -73.9929),
    103: (40.7240, -73.9501), 104: (40.7340, -74.0024), 105: (40.7290, -74.0024),
    106: (40.6207, -74.0851), 107: (40.8224, -73.9568), 108: (40.5901, -73.7951),
    109: (40.6240, -74.1590), 110: (40.8390, -73.9218), 111: (40.7668, -73.9918),
    112: (40.7601, -73.9951), 113: (40.8518, -73.9401), 114: (40.7257, -73.8001),
    115: (40.7112, -73.7601), 116: (40.6118, -73.9626), 117: (40.6579, -73.8379),
    118: (40.7279, -74.0065), 119: (40.8184, -73.8851), 120: (40.7551, -73.8834),
    121: (40.6968, -73.7968), 122: (40.7115, -73.7701), 123: (40.6413, -73.7781),
    124: (40.6479, -73.9757), 125: (40.7073, -73.8301), 126: (40.7207, -73.8201),
    127: (40.8740, -73.9001), 128: (40.7418, -73.9796), 129: (40.7773, -73.8729),
    130: (40.6715, -73.7446), 131: (40.7673, -73.9590), 132: (40.7701, -73.9657),
    133: (40.7740, -73.9834), 134: (40.7779, -73.9879), 135: (40.7218, -73.9965),
    136: (40.7468, -73.9479), 137: (40.7501, -73.9412), 138: (40.7390, -74.0062),
    139: (40.8218, -73.9118), 140: (40.7162, -73.8701), 141: (40.7551, -73.9840),
    142: (40.7568, -73.9740), 143: (40.7634, -73.9796), 144: (40.7490, -73.9890),
    145: (40.6157, -73.9135), 146: (40.5712, -74.1051), 147: (40.8090, -73.9634),
    148: (40.8285, -73.9118), 149: (40.8112, -73.9151), 150: (40.8473, -73.9051),
    151: (40.7490, -73.9765), 152: (40.7540, -73.8218), 153: (40.5718, -74.1134),
    154: (40.7579, -73.8568), 155: (40.8807, -73.8712), 156: (40.7401, -73.7568),
    157: (40.5601, -74.1190), 158: (40.7718, -73.9351), 159: (40.7740, -73.9345),
    160: (40.6804, -73.8501), 161: (40.7612, -73.9715), 162: (40.7501, -73.9940),
    163: (40.8362, -73.8640), 164: (40.8640, -73.8290), 165: (40.8590, -73.8046),
    166: (40.8568, -73.8601), 167: (40.7523, -73.9765), 168: (40.7290, -73.8115),
    169: (40.6354, -74.1240), 170: (40.6585, -73.9557), 171: (40.6779, -73.9671),
    172: (40.6601, -73.9690), 173: (40.7240, -73.7418), 174: (40.7357, -73.8290),
    175: (40.7584, -73.9401), 176: (40.7923, -73.9262), 177: (40.6762, -74.0090),
    178: (40.7234, -73.8618), 179: (40.6979, -73.8318), 180: (40.7018, -73.9001),
    181: (40.7923, -73.8879), 182: (40.9012, -73.9118), 183: (40.5821, -73.8379),
    184: (40.7612, -73.9540), 185: (40.6679, -73.7329), 186: (40.5462, -74.2001),
    187: (40.6890, -73.7640), 188: (40.6423, -74.0779), 189: (40.7490, -73.9001),
    190: (40.7690, -73.9012), 191: (40.5757, -74.0029), 192: (40.6057, -73.7840),
    193: (40.5885, -74.0740), 194: (40.5890, -74.0751), 195: (40.6779, -73.7768),
    196: (40.6712, -73.8201), 197: (40.7104, -73.9576), 198: (40.7104, -73.9576),
    199: (40.6629, -73.7601), 200: (40.6529, -73.7668), 201: (40.6262, -74.0657),
    202: (40.6490, -73.8768), 203: (40.7690, -73.9001), 204: (40.7337, -73.9782),
    205: (40.6829, -73.9240), 206: (40.7584, -73.9651), 207: (40.7579, -73.9857),
    208: (40.7162, -74.0090), 209: (40.7134, -73.9934), 210: (40.7523, -73.9701),
    211: (40.7368, -73.9912), 212: (40.8551, -73.9240), 213: (40.7757, -73.9551),
    214: (40.7668, -73.9601), 215: (40.7945, -73.9718), 216: (40.7840, -73.9801),
    217: (40.9018, -73.8896), 218: (40.8918, -73.8879), 219: (40.8484, -73.8579),
    220: (40.8512, -73.9401), 221: (40.8440, -73.9434), 222: (40.6329, -74.1029),
    223: (40.7512, -74.0029), 224: (40.8284, -73.9240), 225: (40.8368, -73.8812),
    226: (40.7351, -74.0062), 227: (40.8384, -73.8529), 228: (40.6290, -74.1334),
    229: (40.8023, -73.8121), 230: (40.7601, -73.8451), 231: (40.8751, -73.8501),
    232: (40.7218, -73.9576), 233: (40.7134, -73.9543), 234: (40.6557, -73.9779),
    235: (40.6962, -73.8551), 236: (40.8951, -73.8651), 237: (40.7468, -73.9034),
    238: (40.7127, -74.0134), 239: (40.7751, -73.9451), 240: (40.7740, -73.9534),
    241: (40.6379, -73.9073), 242: (40.6679, -73.9812), 243: (40.6040, -74.1129),
    244: (40.5240, -74.2212), 245: (40.5590, -73.9101), 246: (40.6118, -73.8218),
    247: (40.5973, -73.7618), 248: (40.6601, -73.8440), 249: (40.5840, -73.8112),
    250: (40.7290, -73.8662), 251: (40.7240, -74.0029), 252: (40.8101, -73.9601),
    253: (40.6879, -73.8265), 254: (40.6290, -74.0901), 255: (40.6468, -73.9990),
    256: (40.6379, -74.1740), 257: (40.6468, -73.9940), 258: (40.6451, -74.0101),
    259: (40.8679, -73.9218), 260: (40.8784, -73.9196), 261: (40.7127, -74.0134),
    262: (40.7468, -73.9034), 263: (40.7468, -73.8618), 264: (40.7128, -74.0059),
    265: (40.7128, -74.0059),
}

# ============================================================
# HAVERSINE DISTANCE (straight-line miles antar dua koordinat)
# + Road correction factor 1.35 (khas untuk kota urban / NYC)
# ============================================================
ROAD_CORRECTION = 1.35  # faktor koreksi: jarak lurus → estimasi jarak jalan

def haversine_miles(lat1, lon1, lat2, lon2):
    """Hitung jarak great-circle dalam miles."""
    R = 3958.8  # radius bumi dalam miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi    = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * R * math.asin(math.sqrt(a))

def estimate_road_distance(loc_id_1, loc_id_2):
    """Estimasi jarak jalan (miles) antara dua zona NYC berdasarkan centroid."""
    if loc_id_1 == loc_id_2:
        return 0.5  # perjalanan dalam zona yang sama → default 0.5 mi
    coord1 = ZONE_COORDS.get(loc_id_1)
    coord2 = ZONE_COORDS.get(loc_id_2)
    if coord1 is None or coord2 is None:
        return 5.0  # fallback default
    straight = haversine_miles(*coord1, *coord2)
    return round(straight * ROAD_CORRECTION, 1)

# Buat daftar tampilan dropdown zona
def zone_display(loc_id):
    return f"{loc_id} — {NYC_ZONES.get(loc_id, 'Unknown')}"

ZONE_OPTIONS      = sorted(NYC_ZONES.keys())
ZONE_DISPLAY_LIST = [zone_display(i) for i in ZONE_OPTIONS]
ZONE_DISPLAY_TO_ID = {zone_display(i): i for i in ZONE_OPTIONS}

# API Configuration
try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = os.environ.get("API_URL", "http://localhost:8000")

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

# Sidebar
st.sidebar.image("https://images.unsplash.com/photo-1492664738985-f386ad69b38f?auto=format&fit=crop&q=80&w=400", use_column_width=True)
st.sidebar.header("⚙️ Configuration")
st.sidebar.markdown(f"**API Endpoint:** `{API_URL}`")

try:
    health_check = requests.get(f"{API_URL}/")
    if health_check.status_code == 200:
        st.sidebar.success("● API Connected")
    else:
        st.sidebar.warning("⚠ API connected but returned error status.")
except Exception:
    st.sidebar.error("❌ Disconnected from API. Please ensure the backend is running.")

# ── Input Layout ────────────────────────────────────────────
st.markdown("### 📋 Input Ride Details")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("##### 📍 Location Details")

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

    pu_location = ZONE_DISPLAY_TO_ID[pu_display]
    do_location = ZONE_DISPLAY_TO_ID[do_display]

    st.caption(f"📍 Pickup ID: **{pu_location}** | 🏁 Dropoff ID: **{do_location}**")

    st.markdown("##### 💳 Payment & Rate Details")
    payment_type = st.selectbox(
        "Payment Type", [1, 2, 3, 4],
        format_func=lambda x: {1: "Credit Card", 2: "Cash", 3: "No Charge", 4: "Dispute"}[x]
    )
    ratecode_id = st.selectbox(
        "Rate Code ID", [1.0, 2.0, 3.0, 4.0, 5.0, 99.0],
        format_func=lambda x: {
            1.0: "Standard rate", 2.0: "JFK", 3.0: "Newark",
            4.0: "Nassau or Westchester", 5.0: "Negotiated fare", 99.0: "Group ride"
        }[x]
    )

with col2:
    st.markdown("##### 🚘 Trip Profile")
    vendor_id = st.selectbox(
        "Vendor ID", [1, 2],
        format_func=lambda x: "Creative Mobile Technologies (1)" if x == 1 else "VeriFone Inc. (2)"
    )
    passenger_count = st.slider("Passenger Count", min_value=1, max_value=6, value=1)

    # ── Auto-estimate trip distance ──────────────────────────
    zone_pair = (pu_location, do_location)

    # Reset estimasi saat zona berubah; pertahankan jika user sudah edit manual
    if st.session_state.get("_prev_zone_pair") != zone_pair:
        st.session_state["_prev_zone_pair"] = zone_pair
        st.session_state["_auto_dist"] = estimate_road_distance(pu_location, do_location)

    auto_dist = st.session_state.get("_auto_dist", 5.0)

    trip_distance = st.number_input(
        "🗺️ Trip Distance (miles)",
        min_value=0.1,
        max_value=200.0,
        value=float(auto_dist),
        step=0.1,
        help="Estimasi otomatis dari jarak centroid antar zona (×1.35 faktor jalan). Anda bisa ubah manual jika tahu jarak sesungguhnya."
    )

    # Tampilkan info estimasi
    straight_dist = estimate_road_distance(pu_location, do_location) / ROAD_CORRECTION
    st.markdown(
        f'<div class="dist-info">📐 Estimasi dari zona centroid: '
        f'~{straight_dist:.1f} mi lurus × {ROAD_CORRECTION} = <b>~{auto_dist:.1f} mi</b> jalan</div>',
        unsafe_allow_html=True
    )

    store_and_fwd = st.selectbox(
        "Store and Forward Flag", ["N", "Y"],
        help="Did the ride record hold in vehicle memory before sending?"
    )

with col3:
    st.markdown("##### 🕒 Time & Schedule")
    pickup_hour = st.slider("Pickup Hour (24h)", min_value=0, max_value=23, value=14)
    day_of_week = st.selectbox(
        "Day of the Week",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    )
    hour_bucket = st.selectbox("Hour Bucket", ["Late Night", "Regular", "Rush Hour"], index=1)

# ── Predict Button ───────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
predict_btn = st.button("🚀 Predict Fare & Duration", use_container_width=True)

if predict_btn:
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
                ml_res = result.get("ml_model", {})
                dl_res = result.get("dl_model", {})

                st.markdown("### 📊 Prediction Comparison Results")

                # Tampilkan info rute
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.04); border-radius:10px; padding:12px 20px;
                            margin-bottom:16px; border:1px solid rgba(255,255,255,0.08);">
                    <span style="color:#94a3b8; font-size:13px;">ROUTE &nbsp;|&nbsp; {trip_distance:.1f} miles</span><br>
                    <span style="font-size:15px;">
                        🟢 <b>{NYC_ZONES.get(pu_location, pu_location)}</b>
                        &nbsp;→&nbsp;
                        🔴 <b>{NYC_ZONES.get(do_location, do_location)}</b>
                    </span>
                </div>
                """, unsafe_allow_html=True)

                col_ml, col_dl = st.columns(2)

                with col_ml:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">🤖 Machine Learning - {ml_res.get('name')}</div>
                        <div style="display:flex; justify-content:space-between; margin-top:15px;">
                            <div>
                                <p style="margin:0; font-size:14px; color:#888;">ESTIMATED FARE</p>
                                <p class="metric-val">${ml_res.get('predicted_total_amount'):.2f}</p>
                            </div>
                            <div>
                                <p style="margin:0; font-size:14px; color:#888;">ESTIMATED DURATION</p>
                                <p class="metric-val">{ml_res.get('predicted_duration_minutes'):.1f}
                                    <span class="metric-unit">mins</span></p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_dl:
                    st.markdown(f"""
                    <div class="metric-card" style="border-color:rgba(249,217,73,0.3);">
                        <div class="metric-title" style="color:#f9d949;">🧠 Deep Learning - {dl_res.get('name')}</div>
                        <div style="display:flex; justify-content:space-between; margin-top:15px;">
                            <div>
                                <p style="margin:0; font-size:14px; color:#888;">ESTIMATED FARE</p>
                                <p class="metric-val" style="color:#f9d949;">${dl_res.get('predicted_total_amount'):.2f}</p>
                            </div>
                            <div>
                                <p style="margin:0; font-size:14px; color:#888;">ESTIMATED DURATION</p>
                                <p class="metric-val" style="color:#f9d949;">{dl_res.get('predicted_duration_minutes'):.1f}
                                    <span class="metric-unit">mins</span></p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.info("💡 Note: XGBoost (ML) models are generally better suited for tabular feature structures, while Deep Learning models (PyTorch MLP) capture non-linear complex feature combinations after standardized transformations.")

            else:
                st.error(f"Error from API ({response.status_code}): {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to API server: {e}")
