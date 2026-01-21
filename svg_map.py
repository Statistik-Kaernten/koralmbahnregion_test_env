import json
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.ops import transform
from shapely.validation import make_valid
import pyproj
from streamlit.components.v1 import html
from misc.gkzList import *
import html as html_escape

# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------
def polygon_to_path(poly: Polygon) -> str:
    """Convert a Shapely Polygon into a valid SVG path string."""
    parts = []

    # exterior
    coords = list(poly.exterior.coords)
    parts.append(f"M {coords[0][0]} {coords[0][1]}")
    for x, y in coords[1:]:
        parts.append(f"L {x} {y}")
    parts.append("Z")

    # holes
    for ring in poly.interiors:
        coords = list(ring.coords)
        parts.append(f"M {coords[0][0]} {coords[0][1]}")
        for x, y in coords[1:]:
            parts.append(f"L {x} {y}")
        parts.append("Z")

    return " ".join(parts)

def geometry_to_paths(geometry):
    """Safe geometry → list of SVG path strings."""
    # ------------------------------------------------------------
    # PROJECTION: EPSG:4326 → EPSG:3857
    # ------------------------------------------------------------
    transformer = pyproj.Transformer.from_crs(
        "EPSG:4326", "EPSG:3857", always_xy=True
    ).transform
    try:
        geom = shape(geometry)
        geom = make_valid(geom)
        geom = transform(transformer, geom)
    except Exception:
        return []

    paths = []

    if isinstance(geom, Polygon):
        paths.append(polygon_to_path(geom))

    elif isinstance(geom, MultiPolygon):
        for poly in geom.geoms:
            if not poly.is_empty:
                paths.append(polygon_to_path(poly))

    return paths

def color_for_gkz(gkz: str) -> str:
    if gkz in gkzList['gkz']:
        color = "#CC79A7"  # violet
    elif gkz.startswith("2"):
        color = "#FFB81C"  # yellow
    elif gkz.startswith("6"):
        color = "#5B8C5A"  # green
    else:
        color = "#000000"      # fallback
    return color

def safe(text):
    return html_escape.escape(str(text))

# ------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------
def create_svg_map():
    # ------------------------------------------------------------
    # LOAD DATA 
    # ------------------------------------------------------------
    with open("data/koralm2025.json", "r", encoding="utf-8") as f:
        geojson = json.load(f)

    # ------------------------------------------------------------
    # Transform Hitzendorf to a single polygon
    # ------------------------------------------------------------
    for feature in geojson["features"]:
        geom = feature["geometry"]

        if geom["type"] == "MultiPolygon":
            geom["type"] = "Polygon"
            geom["coordinates"] = geom["coordinates"][0]

    # ------------------------------------------------------------
    # BUILD ALL PATHS + COMPUTE BOUNDS
    # ------------------------------------------------------------

    svg_paths = []

    for feature in geojson["features"]:
        gkz = feature["properties"]["Gemeindenummer"]  
        color = color_for_gkz(gkz)

        for d in geometry_to_paths(feature["geometry"]):
            hover_text = f"{feature['properties']['Gemeindename']}"
            svg_paths.append((d, color, hover_text))
            coords = d.replace("M", "").replace("L", "").replace("Z", "").split()

    const = 1
    flipped_svg_paths = []

    for d, color, hover in svg_paths:
        coords = d.replace("M", "").replace("L", "").replace("Z", "").split()
        numbers = list(map(float, coords))
        points = list(zip(numbers[0::2], numbers[1::2]))

        flipped_points = [(x, const - y) for x, y in points]

        parts = [f"M {flipped_points[0][0]} {flipped_points[0][1]}"]
        for x, y in flipped_points[1:]:
            parts.append(f"L {x} {y}")
        parts.append("Z")

        flipped_svg_paths.append((" ".join(parts), color, hover))

    # ------------------------------------------------------------
    # FOUND COORDS BY HAND
    # ------------------------------------------------------------   
    minx = 1381878.1
    miny = -6125037.8
    view_width = 429330.3
    view_height = 416180.5

    # ------------------------------------------------------------
    # RENDER SVG (NO Y-FLIP, NO TRICKS)
    # ------------------------------------------------------------
    svg_content = "\n".join(
    f"""
        <path
        d="{d}"
        fill="{color}"
        stroke="#333"
        stroke-width="500"
        fill-rule="evenodd"
        >
        <title>{hover}</title>
        </path>
        """
        for d, color, hover in flipped_svg_paths
    )

    # ------------------------------------------------------------
    # OPUTPUT THE HTML FOR IMPLEMENTATION
    # ------------------------------------------------------------

    output = html(
        f"""
    <div style="width:100%; max-width:800px; margin:auto;">
    <div style="
        position: relative;
        width: 100%;
        padding-bottom: 100%;   /* 600 / 1000 = 0.6 */
        /*background-color: green;
        border: 2px solid red;*/
    ">
        <svg
        viewBox="{minx} {miny} {view_width} {view_height}"
        preserveAspectRatio="xMidYMid meet"
        style="
            position: absolute;
            top: 0; left: 0;
            width: 100%;
            height: 100%;
        "
        >
        {svg_content}
        </svg>
    </div>
    </div>
    """,
        height=700
    )
    return output

