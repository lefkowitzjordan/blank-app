import streamlit as st
import rasterio
from pyproj import Transformer
import pandas as pd
import numpy as np
import pydeck as pdk

st.set_page_config(page_title="Cancer Risk Factor Lookup", layout="centered")

st.title("Cancer Risk Factor Lookup")
st.markdown("### Welcome! Enter coordinates to get started")

FILE_PATH = "NDVI_california.tif"
CALENV_PATH = "CalEnvScreen.xlsx"


@st.cache_resource
def open_raster(path):
    return rasterio.open(path)


@st.cache_data
def load_calenviro(path):
    return pd.read_excel(path, engine="openpyxl")


def find_nearest_tract(df, lat, lon):
    temp = df.copy()
    temp["distance"] = (
        (temp["Latitude"] - lat) ** 2 +
        (temp["Longitude"] - lon) ** 2
    )
    return temp.loc[temp["distance"].idxmin()]


def fmt3(value):
    if pd.isna(value):
        return "N/A"
    try:
        return f"{float(value):.3g}"
    except Exception:
        return str(value)


calenv_df = load_calenviro(CALENV_PATH)
src = open_raster(FILE_PATH)

to_utm = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
to_wgs84 = Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True)

latlon = st.text_input("Enter latitude,longitude (example: 34.05,-118.25)")

if latlon:
    try:
        lat_str, lon_str = latlon.split(",")
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())

        # --- NDVI lookup ---
        x, y = to_utm.transform(lon, lat)
        sampled = next(src.sample([(x, y)], masked=True))[0]

        row, col = src.index(x, y)
        pixel_x, pixel_y = src.xy(row, col)
        pixel_lon, pixel_lat = to_wgs84.transform(pixel_x, pixel_y)

        ndvi_value = None
        if not getattr(sampled, "mask", False):
            ndvi_value = float(sampled)

        st.subheader("Your NDVI score is")
        st.markdown("**N/A**" if ndvi_value is None else f"**{fmt3(ndvi_value)}**")

        st.markdown(
            f'<span style="color: blue;">Input location: {lat:.6f}, {lon:.6f}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<span style="color: red;">Pixel center: {pixel_lat:.6f}, {pixel_lon:.6f}</span>',
            unsafe_allow_html=True,
        )

        # --- CalEnviroScreen lookup ---
        tract = find_nearest_tract(calenv_df, lat, lon)

        ozone = tract["Ozone"]
        ozone_pctl = tract["Ozone Pctl"]
        pm25 = tract["PM2.5"]
        pm25_pctl = tract["PM2.5 Pctl"]

        st.markdown("### Air Quality Data")

        st.markdown(
            f"Your *daily maximum 8-hour Ozone* concentration is "
            f"**{fmt3(ozone)}** ppm, which is in the **{fmt3(ozone_pctl)}** percentile."
        )

        st.markdown(
            f"Your *annual mean PM2.5* concentration is "
            f"**{fmt3(pm25)}** µg/m³, which is in the **{fmt3(pm25_pctl)}** percentile."
        )

        st.markdown("### Here's a map of your location:")

        map_df = pd.DataFrame(
            [
                {"lat": lat, "lon": lon, "point_type": "input"},
                {"lat": pixel_lat, "lon": pixel_lon, "point_type": "pixel"},
            ]
        )

        input_df = map_df[map_df["point_type"] == "input"]
        pixel_df = map_df[map_df["point_type"] == "pixel"]

        input_layer = pdk.Layer(
            "ScatterplotLayer",
            data=input_df,
            get_position="[lon, lat]",
            get_fill_color=[0, 0, 255, 180],
            get_radius=60,
            pickable=True,
        )

        pixel_layer = pdk.Layer(
            "ScatterplotLayer",
            data=pixel_df,
            get_position="[lon, lat]",
            get_fill_color=[255, 0, 0, 180],
            get_radius=60,
            pickable=True,
        )

        view_state = pdk.ViewState(
            latitude=(lat + pixel_lat) / 2,
            longitude=(lon + pixel_lon) / 2,
            zoom=11,
            pitch=0,
        )

        deck = pdk.Deck(
            layers=[input_layer, pixel_layer],
            initial_view_state=view_state,
            tooltip={"text": "{point_type}\n({lat}, {lon})"},
        )

        st.pydeck_chart(deck)

    except Exception:
        st.error("Please enter coordinates in the format: 34.05,-118.25")