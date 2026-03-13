"""
RoutaGo — Cebu Interactive Map
1st click → Current Location (blue pin)
2nd click → Destination / Where To (red pin) + direction line
3rd click → resets and starts over
"""

import streamlit as st
import folium
import requests
from streamlit_folium import st_folium
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import load_css, render_sidebar, inject_dark_mode

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cebu Map — RoutaGo",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css("assets/styles/main.css")
load_css("assets/styles/map.css")

render_sidebar()
inject_dark_mode()

# ── Session state ─────────────────────────────────────────────────────────────
if "current_loc" not in st.session_state:
    st.session_state.current_loc = None          # {"lat", "lng", "address"}
if "dest_loc" not in st.session_state:
    st.session_state.dest_loc = None             # {"lat", "lng", "address"}

CEBU_CENTER = [10.3157, 123.8854]

# ── Road routing via OSRM (free, no API key) ──────────────────────────────────
def get_road_route(lat1, lng1, lat2, lng2):
    """Fetch actual road geometry from OSRM. Returns [[lat,lng], ...] or None."""
    try:
        resp = requests.get(
            f"http://router.project-osrm.org/route/v1/driving/{lng1},{lat1};{lng2},{lat2}",
            params={"overview": "full", "geometries": "geojson"},
            timeout=8,
        )
        if resp.ok:
            data = resp.json()
            if data.get("code") == "Ok":
                # OSRM returns [lng, lat] — swap for folium
                coords = data["routes"][0]["geometry"]["coordinates"]
                return [[c[1], c[0]] for c in coords]
    except Exception:
        pass
    return None

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="rg-page-header">
    <div class="rg-page-header-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
    </div>
    <div class="rg-page-header-text">
        <h1>Cebu City Map</h1>
        <p>1st click sets your <strong>Current Location</strong> · 2nd click sets your <strong>Destination</strong></p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Status tip ────────────────────────────────────────────────────────────────
cur  = st.session_state.current_loc
dest = st.session_state.dest_loc

if cur is None:
   tip_msg = "Click anywhere on the map to set your <strong>Current Location</strong>"
elif dest is None:
    tip_msg = "Now click your <strong>Destination</strong> on the map"
else:
    tip_msg = "Route pinned. Click anywhere to <strong>start over</strong>"

st.markdown(f"""
<div class="rg-map-tip">
    <span class="rg-map-tip-icon"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg></span>
    <span>{tip_msg}</span>
</div>
""", unsafe_allow_html=True)

# ── Build the Folium map ──────────────────────────────────────────────────────
# Center: if we have pins, center on midpoint; otherwise default Cebu
if cur and dest:
    center = [(cur["lat"] + dest["lat"]) / 2, (cur["lng"] + dest["lng"]) / 2]
elif cur:
    center = [cur["lat"], cur["lng"]]
else:
    center = CEBU_CENTER

m = folium.Map(
    location=center,
    zoom_start=14,
    tiles="OpenStreetMap",
    control_scale=True,
    min_zoom=12,
    max_zoom=19,
    max_bounds=True,
    min_lat=10.20,
    max_lat=10.48,
    min_lon=123.74,
    max_lon=124.02,
)

# Blue marker — Current Location
if cur:
    popup_cur = f"""
    <div style="font-family:Inter,sans-serif;min-width:160px;padding:4px 2px;">
        <div style="font-size:13px;font-weight:700;color:#2563EB;margin-bottom:4px;">🔵 Current Location</div>
        <div style="font-size:12px;color:#374151;line-height:1.5;">{cur['address']}</div>
        <div style="font-size:10px;color:#9CA3AF;margin-top:4px;">{cur['lat']:.5f}, {cur['lng']:.5f}</div>
    </div>
    """
    folium.Marker(
        location=[cur["lat"], cur["lng"]],
        popup=folium.Popup(popup_cur, max_width=240),
        tooltip="🔵 Current Location",
        icon=folium.Icon(color="blue", icon="circle", prefix="fa"),
    ).add_to(m)

# Red marker — Destination
if dest:
    popup_dest = f"""
    <div style="font-family:Inter,sans-serif;min-width:160px;padding:4px 2px;">
        <div style="font-size:13px;font-weight:700;color:#DC2626;margin-bottom:4px;">🔴 Destination</div>
        <div style="font-size:12px;color:#374151;line-height:1.5;">{dest['address']}</div>
        <div style="font-size:10px;color:#9CA3AF;margin-top:4px;">{dest['lat']:.5f}, {dest['lng']:.5f}</div>
    </div>
    """
    folium.Marker(
        location=[dest["lat"], dest["lng"]],
        popup=folium.Popup(popup_dest, max_width=240),
        tooltip="🔴 Destination",
        icon=folium.Icon(color="red", icon="flag", prefix="fa"),
    ).add_to(m)

# Direction lines: road-following via OSRM, split blue→red at midpoint
if cur and dest:
    # Cache road coords so we don't re-fetch on every rerender
    if "road_coords" not in st.session_state:
        with st.spinner("Fetching road route…"):
            st.session_state.road_coords = get_road_route(
                cur["lat"], cur["lng"], dest["lat"], dest["lng"]
            )
    road = st.session_state.road_coords
    if road and len(road) >= 2:
        mid = len(road) // 2
        # Blue segment — origin half (follows roads)
        folium.PolyLine(
            locations=road[:mid + 1],
            color="#2563EB",
            weight=5,
            opacity=0.88,
        ).add_to(m)
        # Red segment — destination half (follows roads)
        folium.PolyLine(
            locations=road[mid:],
            color="#DC2626",
            weight=5,
            opacity=0.88,
        ).add_to(m)
    else:
        # Fallback straight line if OSRM unavailable
        mid_lat = (cur["lat"] + dest["lat"]) / 2
        mid_lng = (cur["lng"] + dest["lng"]) / 2
        folium.PolyLine([[cur["lat"], cur["lng"]], [mid_lat, mid_lng]],
                        color="#2563EB", weight=5, opacity=0.88).add_to(m)
        folium.PolyLine([[mid_lat, mid_lng], [dest["lat"], dest["lng"]]],
                        color="#DC2626", weight=5, opacity=0.88).add_to(m)

# ── Render the map ────────────────────────────────────────────────────────────
map_data = st_folium(
    m,
    height=520,
    use_container_width=True,
    returned_objects=["last_clicked"],
    key="cebu_map",
)

# ── Handle click ──────────────────────────────────────────────────────────────
def reverse_geocode(lat, lng):
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lng, "format": "json"},
            headers={"User-Agent": "RoutaGo-Streamlit-App/1.0"},
            timeout=5,
        )
        if resp.ok:
            return resp.json().get("display_name", f"{lat:.5f}, {lng:.5f}")
    except Exception:
        pass
    return f"Location at {lat:.5f}, {lng:.5f}"

if map_data and map_data.get("last_clicked"):
    clicked = map_data["last_clicked"]
    lat, lng = clicked["lat"], clicked["lng"]

    if cur is None:
        # First click → set current location
        address = reverse_geocode(lat, lng)
        st.session_state.current_loc = {"lat": lat, "lng": lng, "address": address}
        st.session_state.pop("road_coords", None)
        st.rerun()
    elif dest is None:
        # Second click → set destination
        address = reverse_geocode(lat, lng)
        st.session_state.dest_loc = {"lat": lat, "lng": lng, "address": address}
        st.session_state.pop("road_coords", None)
        st.rerun()
    else:
        # Third click → reset everything
        st.session_state.current_loc = None
        st.session_state.dest_loc = None
        st.session_state.pop("road_coords", None)
        st.rerun()

# ── Info cards ────────────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    if cur:
        short = cur["address"].split(",")[0] if "," in cur["address"] else cur["address"][:40]
        st.markdown(f"""
        <div class="rg-map-pin-card rg-pin-current">
            <div class="rg-map-pin-badge rg-badge-blue">🔵 Current</div>
            <div class="rg-map-pin-body">
                <div class="rg-map-pin-name">{short}</div>
                <div class="rg-map-pin-full">{cur['address']}</div>
                <div class="rg-map-pin-coords">{cur['lat']:.5f}° N, {cur['lng']:.5f}° E</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="rg-map-pin-card rg-pin-empty">
            <div class="rg-map-pin-badge rg-badge-blue">🔵 Current</div>
            <div class="rg-map-pin-body">
                <div class="rg-map-pin-name" style="color:#94A3B8;">Not set yet</div>
                <div class="rg-map-pin-full" style="color:#94A3B8;">Click the map to set your current location</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_b:
    if dest:
        short = dest["address"].split(",")[0] if "," in dest["address"] else dest["address"][:40]
        st.markdown(f"""
        <div class="rg-map-pin-card rg-pin-dest">
            <div class="rg-map-pin-badge rg-badge-red">🔴 Destination</div>
            <div class="rg-map-pin-body">
                <div class="rg-map-pin-name">{short}</div>
                <div class="rg-map-pin-full">{dest['address']}</div>
                <div class="rg-map-pin-coords">{dest['lat']:.5f}° N, {dest['lng']:.5f}° E</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="rg-map-pin-card rg-pin-empty">
            <div class="rg-map-pin-badge rg-badge-red">🔴 Destination</div>
            <div class="rg-map-pin-body">
                <div class="rg-map-pin-name" style="color:#94A3B8;">Not set yet</div>
                <div class="rg-map-pin-full" style="color:#94A3B8;">Click the map to set your destination</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

