import streamlit as st
import rasterio
from pyproj import Transformer
import pandas as pd
import pydeck as pdk
import os
import numpy as np

APP_TITLE = "ClearLand"
APP_SUBTITLE = "Environmental insights for informed health decisions"

st.set_page_config(page_title="Cancer Risk Factor Search", layout="wide")

TIF_PATH = "/mount/src/blank-app/NDVI_california.tif"
CALENV_PATH = "CalEnvScreen.xlsx"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --sage:    #4a7c59;
    --sage-lt: #e8f0eb;
    --sky:     #3a7ca5;
    --earth:   #8b6f47;
    --sand:    #f7f3ed;
    --white:   #ffffff;
    --ink:     #1e2d1f;
    --muted:   #6b7c6d;
    --border:  #d8e4d9;
    --radius:  12px;
    --shadow:  0 2px 12px rgba(74,124,89,0.10);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--sand) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
}

#MainMenu, footer, header { visibility: hidden; }

[data-testid="stSidebar"] {
    background: var(--white) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stSidebarNav"] a {
    border-radius: 8px !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    color: var(--muted) !important;
    padding: 0.45rem 0.75rem !important;
    transition: background 0.15s, color 0.15s;
}
[data-testid="stSidebarNav"] a:hover {
    background: var(--sage-lt) !important;
    color: var(--sage) !important;
}
[data-testid="stSidebarNav"] [aria-current="page"] a,
[data-testid="stSidebarNav"] a[aria-selected="true"] {
    background: var(--sage-lt) !important;
    color: var(--sage) !important;
    font-weight: 600 !important;
}

[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarUserContent"] ~ div button,
button[kind="header"] {
    background: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--sage) !important;
    width: 32px !important;
    height: 32px !important;
    padding: 0 !important;
    box-shadow: var(--shadow) !important;
    transition: background 0.15s !important;
}
[data-testid="stSidebarCollapseButton"] button:hover,
button[kind="header"]:hover {
    background: var(--sage-lt) !important;
}

[data-testid="collapsedControl"] {
    background: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="collapsedControl"] button {
    color: var(--sage) !important;
}

[data-testid="stMainBlockContainer"] {
    padding: 0 2rem 3rem 2rem !important;
    max-width: 860px;
}

.page-header {
    background: linear-gradient(135deg, #2d5a3d 0%, #3a7ca5 100%);
    border-radius: var(--radius);
    padding: 2rem 2.25rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
}
.page-header::after {
    content: '';
    position: absolute;
    bottom: -30px; left: 30%;
    width: 120px; height: 120px;
    border-radius: 50%;
    background: rgba(255,255,255,0.04);
}
.page-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.9rem;
    color: #ffffff;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.02em;
}
.page-header p {
    font-size: 0.875rem;
    color: rgba(255,255,255,0.78);
    margin: 0;
    font-weight: 300;
}

.card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.25rem;
    box-shadow: var(--shadow);
}
.card-title {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 1rem;
}

.metrics-row { display: flex; gap: 1rem; flex-wrap: wrap; }
.metric-chip {
    flex: 1;
    min-width: 160px;
    background: var(--sand);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.25rem;
}
.metric-chip .metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.4rem;
}
.metric-chip .metric-value {
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--ink);
    line-height: 1;
}
.metric-chip .metric-pctl {
    font-size: 0.78rem;
    color: var(--muted);
    margin-top: 0.3rem;
}
.chip-sky   { border-left: 4px solid var(--sky); }
.chip-earth { border-left: 4px solid var(--earth); }

.ndvi-score {
    font-family: 'DM Serif Display', serif;
    font-size: 3.2rem;
    color: var(--sage);
    line-height: 1;
    margin: 0.25rem 0 0.25rem 0;
}
.ndvi-sub {
    color: #6b7c6d;
    font-size: 0.82rem;
    margin: 0.4rem 0 0 0;
}
.ndvi-na {
    font-size: 1.2rem;
    color: var(--muted);
    font-style: italic;
}

.legend-row {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 0.75rem;
    font-size: 0.82rem;
    color: var(--muted);
}
.legend-dot {
    display: inline-block;
    width: 10px; height: 10px;
    border-radius: 50%;
    margin-right: 5px;
    vertical-align: middle;
}

[data-testid="stTextInput"] input {
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    background: var(--white) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 0.85rem !important;
    color: var(--ink) !important;
    box-shadow: none !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--sage) !important;
    box-shadow: 0 0 0 3px rgba(74,124,89,0.12) !important;
}
[data-testid="stTextInput"] label {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}

[data-testid="stButton"] button {
    background: var(--sage) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.25rem !important;
    transition: background 0.15s, transform 0.1s !important;
    box-shadow: 0 2px 8px rgba(74,124,89,0.2) !important;
}
[data-testid="stButton"] button:hover {
    background: #3a6347 !important;
    transform: translateY(-1px) !important;
}

[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    font-family: 'DM Sans', sans-serif !important;
}

.img-caption {
    font-size: 0.75rem;
    color: var(--muted);
    text-align: center;
    margin-top: 0.4rem;
    margin-bottom: 0.5rem;
}
.img-caption a {
    color: var(--muted);
    text-decoration: underline;
    text-underline-offset: 2px;
}
.img-caption a:hover {
    color: var(--sage);
}

.did-you-know {
    background: var(--sage-lt);
    border: 1px solid var(--border);
    border-left: 4px solid var(--sage);
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin-top: 0.75rem;
    font-size: 0.9rem;
    color: var(--ink);
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)


# ── Lazy page getters (fixes NameError from forward references) ──────────────
# These functions are only *called* at runtime, after all st.Page objects exist.
def get_home_page():       return home_page
def get_ndvi_page():       return ndvi_page
def get_air_quality_page(): return air_quality_page
def get_resources_page():  return resources_page


# ── Data helpers ─────────────────────────────────────────────────────────────

def download_tif_if_needed():
    if not os.path.exists(TIF_PATH):
        from huggingface_hub import hf_hub_download
        hf_hub_download(
            repo_id="jordanl2/ndvi-data",
            filename="NDVI_california.tif",
            repo_type="dataset",
            local_dir="/tmp",
            token=os.getenv("HF_TOKEN")
        )


@st.cache_resource
def open_raster():
    download_tif_if_needed()
    return rasterio.open(TIF_PATH)


@st.cache_data
def load_calenviro(path):
    return pd.read_excel(path, engine="openpyxl")


@st.cache_data
def compute_ndvi_stats():
    """Read raster tile-by-tile (memory efficient) and return (sorted positive values, mean)."""
    download_tif_if_needed()
    src = rasterio.open(TIF_PATH)
    positive_vals = []
    for _, window in src.block_windows(1):
        block = src.read(1, window=window, masked=True)
        vals = block.compressed()
        vals = vals[vals > 0]
        if len(vals) > 0:
            positive_vals.append(vals)
    all_vals = np.concatenate(positive_vals)
    mean_val = float(np.mean(all_vals))
    sorted_vals = np.sort(all_vals)
    return sorted_vals, mean_val


def ndvi_percentile(ndvi_value: float) -> float:
    sorted_vals, _ = compute_ndvi_stats()
    pct = float(np.searchsorted(sorted_vals, ndvi_value, side='right')) / len(sorted_vals) * 100
    return round(pct, 1)


def ndvi_state_average() -> float:
    _, mean_val = compute_ndvi_stats()
    return round(mean_val, 3)


def find_nearest_tract(df, lat, lon):
    temp = df.copy()
    temp["distance"] = (temp["Latitude"] - lat) ** 2 + (temp["Longitude"] - lon) ** 2
    return temp.loc[temp["distance"].idxmin()]


def fmt3(value):
    if pd.isna(value):
        return "N/A"
    try:
        return f"{float(value):.3g}"
    except Exception:
        return str(value)


def compute_location_data(lat: float, lon: float):
    calenv_df = load_calenviro(CALENV_PATH)
    src = open_raster()
    to_utm = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
    to_wgs84 = Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True)

    x, y = to_utm.transform(lon, lat)
    sampled = next(src.sample([(x, y)], masked=True))[0]

    row, col = src.index(x, y)
    pixel_x, pixel_y = src.xy(row, col)
    pixel_lon, pixel_lat = to_wgs84.transform(pixel_x, pixel_y)

    ndvi_value = None
    ndvi_pctl = None
    if not getattr(sampled, "mask", False):
        ndvi_value = float(sampled)
        if ndvi_value > 0:
            ndvi_pctl = ndvi_percentile(ndvi_value)

    tract = find_nearest_tract(calenv_df, lat, lon)
    ozone = fmt3(tract["Ozone"])
    ozone_pctl = fmt3(tract["Ozone Pctl"])
    pm25 = fmt3(tract["PM2.5"])
    pm25_pctl = fmt3(tract["PM2.5 Pctl"])

    return {
        "lat": lat,
        "lon": lon,
        "pixel_lat": pixel_lat,
        "pixel_lon": pixel_lon,
        "ndvi_value": ndvi_value,
        "ndvi_pctl": ndvi_pctl,
        "ozone": ozone,
        "ozone_pctl": ozone_pctl,
        "pm25": pm25,
        "pm25_pctl": pm25_pctl,
    }


def store_last_result(data: dict):
    st.session_state["last_result"] = data
    st.session_state["last_latlon_text"] = f"{data['lat']:.5f}, {data['lon']:.5f}"


# ── Reusable UI components ───────────────────────────────────────────────────

def render_banner(title: str, desc: str = ""):
    desc_html = f'<p>{desc}</p>' if desc else ''
    st.markdown(
        '<div class="page-header">'
        '<h1>' + title + '</h1>'
        + desc_html +
        '</div>',
        unsafe_allow_html=True,
    )


def render_ndvi_output_card(data: dict):
    ndvi_value = data.get("ndvi_value")
    ndvi_pctl = data.get("ndvi_pctl")
    if ndvi_value is None:
        ndvi_inner = '<div class="ndvi-na">No data available for this location</div>'
    else:
        ndvi_inner = '<div class="ndvi-score">' + fmt3(ndvi_value) + '</div>'
        if ndvi_pctl is not None:
            state_avg = ndvi_state_average()
            ndvi_inner += (
                '<div class="ndvi-sub">'
                f'For context, this is the <strong>{ndvi_pctl}th percentile</strong> for California '
                f'(areas with NDVI &gt; 0). The state average is <strong>{state_avg}</strong>.'
                '</div>'
            )
    st.markdown(
        '<div class="card">'
        '<div class="card-title">Your NDVI output</div>'
        + ndvi_inner +
        '</div>',
        unsafe_allow_html=True,
    )


def render_air_quality_output_card(data: dict):
    st.markdown(
        '<div class="card">'
        '<div class="card-title">Your air quality output</div>'
        '<div class="metrics-row">'
        '<div class="metric-chip chip-sky">'
        '<div class="metric-label">Ozone (8-hr max)</div>'
        '<div class="metric-value">' + data["ozone"] + '</div>'
        '<div class="metric-pctl">ppm &nbsp;&middot;&nbsp; ' + data["ozone_pctl"] + ' percentile</div>'
        '</div>'
        '<div class="metric-chip chip-earth">'
        '<div class="metric-label">PM2.5 (annual mean)</div>'
        '<div class="metric-value">' + data["pm25"] + '</div>'
        '<div class="metric-pctl">&#181;g/m&#179; &nbsp;&middot;&nbsp; ' + data["pm25_pctl"] + ' percentile</div>'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ── Page renderers ───────────────────────────────────────────────────────────

def render_home():
    render_banner(title="Cancer Risk Factor Search")

    st.markdown(
        '<div class="card">'
        '<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0 0 1rem 0;">'
        'Welcome! This Cancer Risk Factor Search tool is designed to help Californians remain informed '
        'about the environment around them – and how it can affect the likelihood and outcome of cancer development.'
        '</p>'
        '<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0 0 1rem 0;">'
        'California is the most <em>populated</em> state, and one of the most <em>polluted</em> ones too. '
        'This means a lot of people are having their health affected by their environment. This tool is based on, '
        'and even pulls data from, existing location-based search tools that provide information about environmental '
        'exposures like the CalEnviroScreen or the EWG\'s Tap Water Database. However, these tools are more focused '
        'on providing <em>data</em> about a variety of exposures, while the goal of the Cancer Risk Factor Search '
        'tool is to take exposure data and provide <em>information</em> about how these relate to a specific health '
        'outcome: cancer.'
        '</p>'
        '<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0;">'
        'Cancer is the second leading cause of death in the US and is the highest NIH-funded disease area. Because '
        'of this, there is a lot of research done on cancer, and for good reason too. But most people do not '
        'understand how the environment around them can relate to cancer in their body, even though modern science '
        'does. Thus, the goal of this tool is to help break down how people could be getting exposed to carcinogens '
        '(cancer-causing chemicals) in their day-to-day life, and provide resources to mitigate these effects. '
        'This tool helps explain these factors, and provides user-specific information about how they exist in '
        '<em>your</em> life, hoping to make this tool even more helpful.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p style="font-size:0.875rem;color:#6b7c6d;margin:0 0 0.5rem 0;">'
        'Enter coordinates to retrieve vegetation, air quality, and environmental risk data for any California location.'
        '</p>',
        unsafe_allow_html=True,
    )

    if "last_latlon_text" in st.session_state and "home_latlon_input" not in st.session_state:
        st.session_state["home_latlon_input"] = st.session_state["last_latlon_text"]

    latlon = st.text_input(
        "Latitude, Longitude",
        placeholder="e.g. 34.05, -118.25",
        key="home_latlon_input",
    )

    if latlon:
        try:
            lat_str, lon_str = latlon.split(",")
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())

            data = compute_location_data(lat, lon)
            store_last_result(data)

            render_ndvi_output_card(data)

            if st.button("What's NDVI?", key="whats_ndvi_btn"):
                st.switch_page(get_ndvi_page())

            render_air_quality_output_card(data)

            if st.button("Learn more about air quality", key="learn_more_air_quality_btn"):
                st.switch_page(get_air_quality_page())

            st.markdown(
                '<div class="card">'
                '<div class="card-title">🗺️ Map</div>'
                '<div class="legend-row">'
                '<span><span class="legend-dot" style="background:#3a7ca5;"></span>'
                'Input location (' + f"{data['lat']:.5f}" + ', ' + f"{data['lon']:.5f}" + ')</span>'
                '<span><span class="legend-dot" style="background:#c0392b;"></span>'
                'Pixel center (' + f"{data['pixel_lat']:.5f}" + ', ' + f"{data['pixel_lon']:.5f}" + ')</span>'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

            map_df = pd.DataFrame([
                {"lat": data["lat"], "lon": data["lon"], "point_type": "Input location"},
                {"lat": data["pixel_lat"], "lon": data["pixel_lon"], "point_type": "Pixel center"},
            ])

            st.pydeck_chart(pdk.Deck(
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=map_df[map_df["point_type"] == "Input location"],
                        get_position="[lon, lat]",
                        get_fill_color=[58, 124, 165, 210],
                        get_radius=80,
                        pickable=True,
                    ),
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=map_df[map_df["point_type"] == "Pixel center"],
                        get_position="[lon, lat]",
                        get_fill_color=[192, 57, 43, 210],
                        get_radius=80,
                        pickable=True,
                    ),
                ],
                initial_view_state=pdk.ViewState(
                    latitude=(data["lat"] + data["pixel_lat"]) / 2,
                    longitude=(data["lon"] + data["pixel_lon"]) / 2,
                    zoom=11,
                    pitch=0,
                ),
                tooltip={"text": "{point_type}\n({lat}, {lon})"},
                map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            ))

        except Exception:
            st.error("Please enter coordinates in the format: 34.05, -118.25")

    if st.button("📋 Resources", key="resources_from_home_btn"):
        st.switch_page(get_resources_page())


def render_ndvi():
    render_banner(
        title="What is NDVI?",
        desc="Understanding the Normalized Difference Vegetation Index",
    )

    if "last_result" in st.session_state:
        render_ndvi_output_card(st.session_state["last_result"])
    else:
        st.info("Enter coordinates on the Home page to see your NDVI output here.")

    st.markdown(
        '<div class="card">'
        '<div class="card-title">📖 Definition</div>'
        '<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;">'
        'NDVI stands for <strong>Normalized Difference Vegetation Index</strong>. This metric is used to tell '
        'how much vegetation (aka living plants) are in a given area. NDVI values are calculated using satellite '
        'images that compare the amount of light that plants absorb versus reflect.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.image("NDVI.webp", use_container_width=True)
    st.markdown(
        '<p class="img-caption">'
        '<a href="https://eos.com/blog/normalized-difference-vegetation-index-or-ndvi/" '
        'target="_blank" rel="noopener noreferrer">Image source: EOS Data Analytics</a>'
        '</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="card-title">📊 Understanding NDVI Values</div>'
        '<p style="font-size:0.88rem;color:#6b7c6d;margin:0 0 0.85rem 0;">NDVI values range from &minus;1 to 1:</p>'
        '<div style="display:flex;flex-direction:column;gap:0.6rem;">'
        '<div style="display:flex;align-items:flex-start;gap:0.85rem;padding:0.75rem 1rem;background:#e6f1f8;border-radius:8px;border-left:4px solid #3a7ca5;">'
        '<span style="font-size:1.1rem;">💧</span>'
        '<div><div style="font-size:0.78rem;font-weight:600;color:#3a7ca5;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.2rem;">Negative values</div>'
        '<div style="font-size:0.9rem;color:#1e2d1f;">Water (bodies of water, clouds, or snow)</div></div>'
        '</div>'
        '<div style="display:flex;align-items:flex-start;gap:0.85rem;padding:0.75rem 1rem;background:#f5efe6;border-radius:8px;border-left:4px solid #8b6f47;">'
        '<span style="font-size:1.1rem;">🏜️</span>'
        '<div><div style="font-size:0.78rem;font-weight:600;color:#8b6f47;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.2rem;">Values near zero</div>'
        '<div style="font-size:0.9rem;color:#1e2d1f;">Limited vegetation, bare soil</div></div>'
        '</div>'
        '<div style="display:flex;align-items:flex-start;gap:0.85rem;padding:0.75rem 1rem;background:#e8f0eb;border-radius:8px;border-left:4px solid #4a7c59;">'
        '<span style="font-size:1.1rem;">🌿</span>'
        '<div><div style="font-size:0.78rem;font-weight:600;color:#4a7c59;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.2rem;">Positive values</div>'
        '<div style="font-size:0.9rem;color:#1e2d1f;">Lots of healthy vegetation</div></div>'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="card-title">🔬 NDVI &amp; Cancer Research</div>'
        '<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0 0 1rem 0;">'
        'Increased NDVI has been found to be protective against cancer mortality. This relationship has been '
        'indicated for cancers such as breast cancer, bladder cancer, skin cancer, but especially for prostate '
        'and lung cancer.'
        '</p>'
        '<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0 0 1rem 0;">'
        '<a href="https://www.sciencedirect.com/science/article/pii/S016041202500563X?ref=pdf_download&fr=RR-2&rr=9f0333456b4c2ab4" '
        'target="_blank" rel="noopener noreferrer" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
        'In one study</a>, patients with prostate cancer who did not undergo surgery had an increased likelihood '
        'of mortality. But patients residing in areas with medium NDVI values (0.217&ndash;0.278) had a '
        'significantly decreased risk of mortality, and patients in areas with high NDVI values (&gt;0.278) '
        'had an even lower risk.'
        '</p>'
        '<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;">'
        'Overall, NDVI values greater than 3 were shown to correlate with a decrease in mortality risk across '
        'all cancers. Additionally, increases in NDVI (more vegetation) over time have shown to be protective. '
        'So, promoting wildlife and nature growth can be important for your health!'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.image("Wellness.jpeg", use_container_width=True)
    st.markdown(
        '<p class="img-caption">'
        '<a href="https://www.earth.com/news/nature-boosts-health-well-being/" '
        'target="_blank" rel="noopener noreferrer">Image source: earth.com</a>'
        '</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card" style="background:#e8f0eb;border-color:#4a7c59;">'
        '<div class="card-title" style="color:#4a7c59;">📚 Learn More</div>'
        '<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;">'
        'For more information on NDVI with respect to cancer, we recommend that you '
        '<a href="https://link-springer-com.libproxy2.usc.edu/content/pdf/10.1007/s11356-023-28461-5.pdf" '
        'target="_blank" rel="noopener noreferrer" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
        'check out this study</a> that summarizes the research that has been done on the topic. '
        'Please note that increased NDVI can by no means completely cure or prevent cancer.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button("← Back to Home", key="back_to_home_btn"):
        st.switch_page(get_home_page())
    if st.button("📋 Resources", key="resources_from_ndvi_btn"):
        st.switch_page(get_resources_page())


def render_air_quality():
    render_banner(
        title="Air Quality",
        desc="How air quality affects cancer outcomes",
    )

    if "last_result" in st.session_state:
        render_air_quality_output_card(st.session_state["last_result"])
    else:
        st.info("Enter coordinates on the Home page to see your air quality output here.")

    st.markdown(
        '<div class="card">'
        '<div class="card-title">Ozone</div>'
        '<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;">'
        '<strong>What is Ozone?</strong><br>'
        'Ozone, also known as O3, is a highly reactive gas molecule made up of 3 oxygen atoms. For comparison, '
        'the typical oxygen we breathe is O2, with only two oxygen atoms. As much as extra oxygen may sound good, '
        'this molecule is not stable and can negatively affect the body.<br><br>'
        'Ozone is a natural component of the upper atmosphere, but ground-level ozone, which is the ozone that '
        'exists where we live and breathe, is not so natural. Ground-level ozone is formed by reactions in the '
        'air with nitrogen oxides, volatile organic compounds, and sunlight. The former two are air pollutants, '
        'entering the atmosphere through processes such as industrial facility emissions, gasoline vapor, exhaust '
        'from cars and other vehicles, and even electric utilities! Thus, all of these processes can increase '
        'ozone in the air we breathe.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.image("Ozone1.png", use_container_width=True)
    st.markdown(
        '<p class="img-caption">'
        '<a href="https://www.khanacademy.org/science/ap-college-environmental-science/x0b0e430a38ebd23f:gl" '
        'target="_blank" rel="noopener noreferrer">Image source: Khan Academy</a>'
        '</p>',
        unsafe_allow_html=True,
    )

    st.image("Ozone2.png", use_container_width=True)
    st.markdown(
        '<p class="img-caption">'
        '<a href="https://otcair.org/about-ozone" '
        'target="_blank" rel="noopener noreferrer">Image source: Ozone Transport Commission</a>'
        '</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="card-title">Ozone and Cancer</div>'
        '<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;">'
        'Ozone has drastic effects on cancer outcomes. Lung cancer, kidney cancer, breast cancer, prostate cancer, '
        'and even brain cancer are just a few of the cancers that ozone can affect. It was found that a '
        '10 &micro;g/m\u00b3 (or 0.0051 ppm, the metric we use to measure ozone on this site) increase in ozone '
        'over a 3-day period can increase cancer mortality by 1%. This effect is especially pronounced during '
        'warmer times of the year. Ozone has such a strong effect on cancer mortality that ozone exposure had a '
        'significant effect on the likelihood of cancer death up to two days before the death.<br><br>'
        'To learn more about lung cancer and ozone, check out some other relevant studies on:<br>'
        '&bull; <a href="https://www.nature.com/articles/s41370-019-0135-4" '
        'target="_blank" rel="noopener noreferrer" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
        'Long-term ozone exposure</a><br>'
        '&bull; <a href="https://onlinelibrary-wiley-com.libproxy1.usc.edu/doi/full/10.1002/ijc.35069" '
        'target="_blank" rel="noopener noreferrer" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
        'Short-term ozone exposure</a><br>'
        '&bull; <a href="https://ascopost.com/news/january-2026/associations-found-between-air-pollutants-and-lung-cancer-subtypes/" '
        'target="_blank" rel="noopener noreferrer" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
        'Air pollution and lung cancer</a>'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="card-title">PM2.5</div>'
        '<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;">'
        '<strong>What is PM2.5?</strong><br>'
        'PM2.5 stands for particulate matter 2.5. These are microscopic particles with diameters less than '
        '2.5 &micro;m, which is 30 times smaller than a human hair!<br>'
        'These particles come from construction sites, sources of fire/smoke, unpaved roads, and chemical '
        'reactions in the atmosphere with other air pollutants, like SO2 and NO.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.image("PM2.5.jpg", use_container_width=True)
    st.markdown(
        '<p class="img-caption">'
        '<a href="https://www.epa.gov/pm-pollution/particulate-matter-pm-basics" '
        'target="_blank" rel="noopener noreferrer">Image source: Environmental Protection Agency</a>'
        '</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="card-title">PM2.5 and Cancer</div>'
        '<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;">'
        'Increased PM2.5 values were found to independently predict a decrease in '
        '<a href="https://www-sciencedirect-com.libproxy1.usc.edu/science/article/pii/S0013935126007759?via%3Dihub" '
        'target="_blank" rel="noopener noreferrer" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
        'breast cancer survival</a>. This pattern was tracked to have an increased hazard ratio (an indication '
        'of risk) by 1.144 per 1 &micro;g/m\u00b3 increase of PM2.5 concentration. These effects are especially '
        'pronounced for older patients (65 years or older) as well as those in earlier stages of cancer diagnosis '
        '(stages I and II).<br><br>'
        '<a href="https://pubs-acs-org.libproxy1.usc.edu/doi/pdf/10.1021/acs.est.4c10986" '
        'target="_blank" rel="noopener noreferrer" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
        'Another study</a> found that PM2.5 levels have a drastic effect on the incidence (aka development) of '
        'all gastrointestinal (GI) cancers. Specifically, the adjusted hazard ratio for a 1 standard deviation '
        'increase in PM2.5 mass is 1.367 for all GI cancers.<br><br>'
        'The most studied cancer with relation to PM2.5 is lung cancer, as PM2.5 enters the body through the '
        'lungs. <a href="https://oce-ovid-com.libproxy1.usc.edu/article/00008469-202211000-00006/PDF" '
        'target="_blank" rel="noopener noreferrer" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
        'One study</a> found that a 10 &micro;g/m\u00b3 increase in PM2.5 related to a 7.95% increase in lung '
        'cancer mortality, with more significant effects on men and older folks (65 years or older).<br><br>'
        'To learn more about lung cancer and PM2.5, check out some other relevant studies on:<br>'
        '&bull; <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC6915823/pdf/kwx166.pdf" '
        'target="_blank" rel="noopener noreferrer" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
        'Long-term PM2.5 exposure in U.S. adults</a><br>'
        '&bull; <a href="https://onlinelibrary-wiley-com.libproxy1.usc.edu/doi/full/10.1002/tox.22437" '
        'target="_blank" rel="noopener noreferrer" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
        'How PM2.5 causes lung cancer</a><br>'
        '&bull; <a href="https://www-sciencedirect-com.libproxy1.usc.edu/science/article/pii/S0048969717317643" '
        'target="_blank" rel="noopener noreferrer" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
        'PM2.5 and male lung cancer</a><br>'
        '&bull; <a href="https://www.proquest.com/docview/3307473046?accountid=14749&parentSessionId=ebTcDAjx0wcSqNJ6ZPbbZyurTyde0SdRnOJayaC237A%3D&pq-origsite=primo&sourcetype=Scholarly%20Journals" '
        'target="_blank" rel="noopener noreferrer" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
        'PM2.5 and lung cancer ecology</a>'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.image("Traffic.webp", use_container_width=True)
    st.markdown(
        '<p class="img-caption">'
        '<a href="https://cepr.org/voxeu/columns/road-traffic-flow-and-air-pollution-concentrations-evidence-japan" '
        'target="_blank" rel="noopener noreferrer">Image source: Centre for Economic Policy Research</a>'
        '</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="did-you-know">'
        '💡 <strong>Did you know:</strong> Areas with a lot of traffic are more likely to have ozone and PM2.5 air pollution.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card" style="background:#e8f0eb;border-color:#4a7c59;margin-top:1.25rem;">'
        '<div class="card-title" style="color:#4a7c59;">More resources</div>'
        '<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;">'
        'To get a more comprehensive understanding of your air quality and environmental health hazards, we '
        'encourage you to check out '
        '<a href="https://oehha.ca.gov/calenviroscreen/report/calenviroscreen-40" '
        'target="_blank" rel="noopener noreferrer" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
        'CalEnviroScreen 4.0</a>. This is a tool put together by the California Office of Environmental Health '
        'Hazard Assessment. It is similar to this tool in that it allows you to look up information for your '
        'area, but with some different parameters as our tool focuses on cancer risk, rather than overall air health.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button("← Back to Home", key="back_to_home_air_quality_btn"):
        st.switch_page(get_home_page())
    if st.button("📋 Resources", key="resources_from_air_quality_btn"):
        st.switch_page(get_resources_page())


def render_resources():
    render_banner(
        title="Resources",
        desc="Steps you can take to reduce your environmental cancer risk",
    )

    st.markdown(
        '<div class="card">'
        '<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0;">'
        'We understand that much of the data provided in this tool mentions things that are out of your control, '
        'and a mere result of where you live. We know that completely moving to a new place with a healthier '
        'environment is completely unfeasible for many people (nor should a single website like this encourage '
        'you to make such a big decision). So here are some things you can control in light of your environmental '
        'cancer risk factors.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="card-title">🌿 NDVI</div>'
        '<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0 0 1rem 0;">'
        'You may not be able to change the local vegetation around you, but that doesn\'t mean you can\'t expose '
        'yourself to more greenspaces. Making an effort to spend more time outdoors, especially in local parks or '
        'forests is a great idea, and can benefit your health. Community resources like hiking groups, run clubs, '
        'community gardens, or any other nature-friendly organization can be a great way to get yourself spending '
        'more time in greenspaces.'
        '</p>'
        '<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0;">'
        'You can also bring the greenspace to you! Getting some houseplants or starting a garden in your backyard '
        'can provide some of the mental benefits of being in nature, and can even help make the air around you '
        'cleaner! Additionally, growing fruits and vegetables at home is a cost-effective way to get clean, '
        'organic food while also exposing yourself to more greenery.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card">'
        '<div class="card-title">💨 Air Quality</div>'
        '<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0 0 1rem 0;">'
        'As much as air quality can seem pervasive, there are many things you can do to reduce your exposure to '
        'pollutants. One great way is to invest in high-quality, up-to-date air filters for your HVAC system at '
        'home, and/or portable air purification systems (i.e. HEPA filters). This can help prevent air pollutants '
        'from entering your home, and remove them out once they do. For more information about air filters, check '
        'out the <a href="https://www.epa.gov/indoor-air-quality-iaq/guide-air-cleaners-home" '
        'target="_blank" rel="noopener noreferrer" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
        'EPA\'s Guide to Air Cleaners in the Home</a>.'
        '</p>'
        '<p style="font-size:0.95rem;line-height:1.75;color:#1e2d1f;margin:0;">'
        'Other ways to reduce air pollution exposure are to keep in mind the sources of air pollution, such as '
        'industrial processes or traffic. If you live off of a busy street, or by a construction site or other '
        'source of air pollution, it is a good idea to limit open windows in your home, especially during active '
        'hours. Moreover, if you find yourself sitting in traffic, closing the windows in your car can reduce '
        'exposure. If you do go outside into an area with heavy air pollution, wearing a face mask can help '
        'relieve any discomfort/smells, and reduce exposure.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button("← Back to Home", key="back_to_home_resources_btn"):
        st.switch_page(get_home_page())


# ── Page registration (must come after all render functions) ─────────────────
home_page = st.Page(render_home, title="Home", default=True)
ndvi_page = st.Page(render_ndvi, title="NDVI")
air_quality_page = st.Page(render_air_quality, title="Air Quality")
resources_page = st.Page(render_resources, title="Resources")

pg = st.navigation([home_page, ndvi_page, air_quality_page, resources_page])
pg.run()