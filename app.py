import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Lab 7 - Interactive Maps", layout="wide")

SHAPEFILE = "ne_110m_admin_0_countries.shp"

# Projections used in the "Geo Projection" example (the lab PDF never defines this dictionary)
projection_options = {
    "Plate Carree (EPSG:4326)": "EPSG:4326",
    "Web Mercator (EPSG:3857)": "EPSG:3857",
    "Robinson": "+proj=robin",
    "Mollweide": "+proj=moll",
    "Equal Earth": "+proj=eqearth",
    "Eckert IV": "+proj=eck4",
}


@st.cache_data
def load_data():
    gdf = gpd.read_file(SHAPEFILE)
    # Natural Earth columns are UPPERCASE (NAME, POP_EST), so normalise to lowercase
    gdf.columns = gdf.columns.str.lower()
    if "pop_est" not in gdf.columns:
        np.random.seed(0)
        gdf["pop_est"] = np.random.randint(1e6, 1e9, size=len(gdf))
    # Area in km2 using an equal-area projection (area in degrees is meaningless)
    gdf["area_km2"] = gdf.to_crs("EPSG:6933").area / 1e6
    gdf["pop_density"] = gdf["pop_est"] / gdf["area_km2"]
    return gdf


gdf = load_data()

st.title("Interactive Map Visualization Examples")
st.sidebar.header("Choose a Map Type")
map_type = st.sidebar.radio(
    "Select Map Type",
    ["Map Cosmetics", "Map Visual Hierarchy", "Choropleth Map", "Geo Projection"],
)

# 1. Map Cosmetics
if map_type == "Map Cosmetics":
    fig, ax = plt.subplots(figsize=(10, 6))
    gdf.plot(ax=ax, color="skyblue", edgecolor="black", linewidth=0.5)
    ax.set_title("Styled Map Example", fontsize=15, fontweight="bold")
    ax.set_facecolor("lightgrey")
    st.pyplot(fig)

# 2. Map Visual Hierarchy
elif map_type == "Map Visual Hierarchy":
    highlighted = st.multiselect(
        "Select countries to highlight in red",
        sorted(gdf["name"].unique()),
        default=["Brazil", "India", "China", "Australia", "South Africa", "Russia"],
    )
    colors = gdf["name"].apply(lambda x: "red" if x in highlighted else "skyblue")
    fig, ax = plt.subplots(figsize=(10, 6))
    gdf.plot(color=colors, edgecolor="black", linewidth=0.5, ax=ax)
    ax.set_title("Map Visual Hierarchy with Selected Countries Highlighted in Red")
    st.pyplot(fig)

# 3. Choropleth Map
elif map_type == "Choropleth Map":
    color_choice = st.selectbox(
        "Choose Color Scheme", ["OrRd", "YlGn", "Blues", "Purples", "Greens"], index=0
    )
    use_log_scale = st.checkbox("Use Log Transformation", value=True)
    data = gdf.copy()
    if use_log_scale:
        data["pop_density"] = np.log1p(data["pop_density"])
    fig, ax = plt.subplots(figsize=(10, 6))
    data.plot(column="pop_density", cmap=color_choice, edgecolor="black",
              legend=True, ax=ax)
    ax.set_title(f"Population Density by Country (Color Scheme: {color_choice})")
    st.pyplot(fig)

# 4. Geo Projection
elif map_type == "Geo Projection":
    proj_choice = st.selectbox("Select a Projection", list(projection_options.keys()))
    color_choice = st.selectbox(
        "Choose Color Scheme", ["OrRd", "YlGn", "Blues", "Purples", "Greens"], index=0
    )
    use_log_scale = st.checkbox("Use Log Transformation for Population Density", value=True)
    data = gdf.copy()
    if use_log_scale:
        data["pop_density"] = np.log1p(data["pop_density"])
    if "3857" in projection_options[proj_choice]:
        data = data[data["name"] != "Antarctica"]  # Mercator blows up at the pole
    data_proj = data.to_crs(projection_options[proj_choice])
    fig, ax = plt.subplots(figsize=(10, 6))
    data_proj.plot(column="pop_density", cmap=color_choice, edgecolor="black",
                   legend=True, ax=ax)
    ax.set_title(f"Map in {proj_choice} Projection")
    st.pyplot(fig)
