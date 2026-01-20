import json

import pydeck as pdk
from misc.gkzList import *

def createDeck():
    # Load GeoJSON
    with open("data/koralm2025.json", encoding="utf-8") as f:
        geojson = json.load(f)

    gkz_List = set(gkzList["gkz"])

    for f in geojson["features"]:
        gkz = str(f["properties"].get("Gemeindenummer", ""))
        if gkz in gkz_List:
            f["properties"]["color"] = [204, 121, 167, 180]
        elif gkz.startswith("2"):
            f["properties"]["color"] = [255, 184, 28, 180]
        else:
            f["properties"]["color"] = [91, 140, 90, 180]

    # PyDeck GeoJsonLayer
    layer = pdk.Layer(
        "GeoJsonLayer",
        geojson,
        pickable=True,
        stroked=True,
        filled=True,
        extruded=False,
        get_fill_color="properties.color",   
        get_line_color=[0, 0, 0, 200],
        line_width_min_pixels=1,
    )


    views = [
        pdk.View(
            type="OrthographicView",
            controller=False
        )
    ]

    view_state = pdk.ViewState(
        latitude=47.0,
        longitude=14.0,
        zoom=7,
        min_zoom=7,
        max_zoom=7,
        pitch=0,
        bearing=0,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="light_no_labels",  
        map_provider=None,
        #views=views,
        tooltip={
            "html": "<b>{Gemeindename}</b>  ",
            "style": {"backgroundColor": "white", "color": "black"},
        },
    )
    return deck

