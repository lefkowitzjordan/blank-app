import streamlit as st
import rasterio
from pyproj import Transformer
import pandas as pd
import pydeck as pdk
import os
import requests

APP_TITLE = "ClearLand"
APP_SUBTITLE = "Environmental insights for informed health decisions"

st.set_page_config(page_title="Cancer Risk Factor Search", layout="wide")

TIF_PATH = "/tmp/NDVI_california.tif"
CALENV_PATH = "CalEnvScreen.xlsx"
GDRIVE_FILE_ID = "1DT6BEr3buUEUtfU6xqlwWjjf0d4-2sqQ"

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
</style>
""", unsafe_allow_html=True)


def download_tif_if_needed():
    if not os.path.exists(TIF_PATH):
        session = requests.Session()
        url = f"https://drive.google.com/uc?export=download&id={GDRIVE_FILE_ID}"
        r = session.get(url, stream=True)
        for key, value in r.cookies.items():
            if key.startswith("download_warning"):
                r = session.get(url + "&confirm=" + value, stream=True)
        with open(TIF_PATH, "wb") as f:
            for chunk in r.iter_content(32768):
                if chunk:
                    f.write(chunk)


@st.cache_resource
def open_raster():
    download_tif_if_needed()
    return rasterio.open(TIF_PATH)


@st.cache_data
def load_calenviro(path):
    return pd.read_excel(path, engine="openpyxl")


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


def render_banner(title: str, desc: str):
    st.markdown(
        '<div class="page-header">'
        '<h1>' + title + '</h1>'
        '<p>' + desc + '</p>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_home():
    render_banner(
        title="Cancer Risk Factor Search",
        desc="Enter coordinates to retrieve vegetation, air quality, and environmental risk data for any California location."
    )

    calenv_df = load_calenviro(CALENV_PATH)
    src = open_raster()
    to_utm   = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
    to_wgs84 = Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True)

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

            x, y = to_utm.transform(lon, lat)
            sampled = next(src.sample([(x, y)], masked=True))[0]

            row, col = src.index(x, y)
            pixel_x, pixel_y = src.xy(row, col)
            pixel_lon, pixel_lat = to_wgs84.transform(pixel_x, pixel_y)

            ndvi_value = None
            if not getattr(sampled, "mask", False):
                ndvi_value = float(sampled)

            if ndvi_value is None:
                ndvi_inner = '<div class="ndvi-na">No data available for this location</div>'
            else:
                ndvi_inner = (
                    '<div class="ndvi-score">' + fmt3(ndvi_value) + '</div>'
                    '<p class="ndvi-sub">Normalized Difference Vegetation Index &nbsp;&middot;&nbsp; &minus;1 to +1 scale</p>'
                )

            st.markdown(
                '<div class="card">'
                '<div class="card-title">🌿 Vegetation Index (NDVI)</div>'
                + ndvi_inner +
                '</div>',
                unsafe_allow_html=True,
            )

            if st.button("What's NDVI?", key="whats_ndvi_btn"):
                st.switch_page(ndvi_page)

            tract      = find_nearest_tract(calenv_df, lat, lon)
            ozone      = fmt3(tract["Ozone"])
            ozone_pctl = fmt3(tract["Ozone Pctl"])
            pm25       = fmt3(tract["PM2.5"])
            pm25_pctl  = fmt3(tract["PM2.5 Pctl"])

            st.markdown(
                '<div class="card">'
                '<div class="card-title">💨 Air Quality</div>'
                '<div class="metrics-row">'
                '<div class="metric-chip chip-sky">'
                '<div class="metric-label">Ozone (8-hr max)</div>'
                '<div class="metric-value">' + ozone + '</div>'
                '<div class="metric-pctl">ppm &nbsp;&middot;&nbsp; ' + ozone_pctl + ' percentile</div>'
                '</div>'
                '<div class="metric-chip chip-earth">'
                '<div class="metric-label">PM2.5 (annual mean)</div>'
                '<div class="metric-value">' + pm25 + '</div>'
                '<div class="metric-pctl">&#181;g/m&#179; &nbsp;&middot;&nbsp; ' + pm25_pctl + ' percentile</div>'
                '</div>'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="card">'
                '<div class="card-title">🗺️ Map</div>'
                '<div class="legend-row">'
                '<span><span class="legend-dot" style="background:#3a7ca5;"></span>'
                'Input location (' + f"{lat:.5f}" + ', ' + f"{lon:.5f}" + ')</span>'
                '<span><span class="legend-dot" style="background:#c0392b;"></span>'
                'Pixel center (' + f"{pixel_lat:.5f}" + ', ' + f"{pixel_lon:.5f}" + ')</span>'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

            map_df = pd.DataFrame([
                {"lat": lat,       "lon": lon,       "point_type": "Input location"},
                {"lat": pixel_lat, "lon": pixel_lon, "point_type": "Pixel center"},
            ])

            st.pydeck_chart(pdk.Deck(
                layers=[
                    pdk.Layer("ScatterplotLayer",
                              data=map_df[map_df["point_type"] == "Input location"],
                              get_position="[lon, lat]",
                              get_fill_color=[58, 124, 165, 210],
                              get_radius=80, pickable=True),
                    pdk.Layer("ScatterplotLayer",
                              data=map_df[map_df["point_type"] == "Pixel center"],
                              get_position="[lon, lat]",
                              get_fill_color=[192, 57, 43, 210],
                              get_radius=80, pickable=True),
                ],
                initial_view_state=pdk.ViewState(
                    latitude=(lat + pixel_lat) / 2,
                    longitude=(lon + pixel_lon) / 2,
                    zoom=11, pitch=0,
                ),
                tooltip={"text": "{point_type}\n({lat}, {lon})"},
                map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            ))

        except Exception:
            st.error("Please enter coordinates in the format: 34.05, -118.25")


def render_ndvi():
    render_banner(
        title="What is NDVI?",
        desc="Understanding the Normalized Difference Vegetation Index"
    )

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

    st.markdown(
        '<div class="card">'
        '<div class="card-title">📊 Understanding NDVI Values</div>'
        '<p style="font-size:0.88rem;color:#6b7c6d;margin:0 0 0.85rem 0;">NDVI values range from &minus;1 to 1:</p>'
        '<div style="display:flex;flex-direction:column;gap:0.6rem;">'

        '<div style="display:flex;align-items:flex-start;gap:0.85rem;padding:0.75rem 1rem;'
        'background:#e6f1f8;border-radius:8px;border-left:4px solid #3a7ca5;">'
        '<span style="font-size:1.1rem;">💧</span>'
        '<div><div style="font-size:0.78rem;font-weight:600;color:#3a7ca5;text-transform:uppercase;'
        'letter-spacing:0.07em;margin-bottom:0.2rem;">Negative values</div>'
        '<div style="font-size:0.9rem;color:#1e2d1f;">Water (bodies of water, clouds, or snow)</div></div>'
        '</div>'

        '<div style="display:flex;align-items:flex-start;gap:0.85rem;padding:0.75rem 1rem;'
        'background:#f5efe6;border-radius:8px;border-left:4px solid #8b6f47;">'
        '<span style="font-size:1.1rem;">🏜️</span>'
        '<div><div style="font-size:0.78rem;font-weight:600;color:#8b6f47;text-transform:uppercase;'
        'letter-spacing:0.07em;margin-bottom:0.2rem;">Values near zero</div>'
        '<div style="font-size:0.9rem;color:#1e2d1f;">Limited vegetation, bare soil</div></div>'
        '</div>'

        '<div style="display:flex;align-items:flex-start;gap:0.85rem;padding:0.75rem 1rem;'
        'background:#e8f0eb;border-radius:8px;border-left:4px solid #4a7c59;">'
        '<span style="font-size:1.1rem;">🌿</span>'
        '<div><div style="font-size:0.78rem;font-weight:600;color:#4a7c59;text-transform:uppercase;'
        'letter-spacing:0.07em;margin-bottom:0.2rem;">Positive values</div>'
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
        'target="_blank" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
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

    st.markdown(
        '<div class="card" style="background:#e8f0eb;border-color:#4a7c59;">'
        '<div class="card-title" style="color:#4a7c59;">📚 Learn More</div>'
        '<p style="font-size:0.95rem;line-height:1.7;color:#1e2d1f;margin:0;">'
        'For more information on NDVI with respect to cancer, we recommend that you '
        '<a href="https://link-springer-com.libproxy2.usc.edu/content/pdf/10.1007/s11356-023-28461-5.pdf" '
        'target="_blank" style="color:#4a7c59;font-weight:600;text-decoration:underline;text-underline-offset:3px;">'
        'check out this study</a> that summarizes the research that has been done on the topic. '
        'Please note that increased NDVI can by no means completely cure or prevent cancer.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button("← Back to Home", key="back_to_home_btn"):
        st.switch_page(home_page)


home_page = st.Page(render_home, title="Home", default=True)
ndvi_page = st.Page(render_ndvi, title="NDVI")

pg = st.navigation([home_page, ndvi_page])
pg.run()