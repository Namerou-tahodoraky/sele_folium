import copy
import folium
import folium.plugins
import pyproj
from typing import Optional, Union
from .utils import (
    create_base_map,
    adjust_zoom_level,
    get_lefttop_coord,
    get_rightbottom_coord,
    get_center_coord_by_area_size,
    )


geod = pyproj.Geod(ellps="WGS84")


def create_map_display_point_moving_anytime(
        coords: list[tuple[float, float]],
    ) -> "folium.Map":
    if not coords:
        raise
    coords = copy.deepcopy(coords)

    start_zoom_level = adjust_zoom_level(
        left_top_latlon=get_lefttop_coord(coords),
        right_bottom_latlon=get_rightbottom_coord(coords),
        width_map_size_pix=512,
        height_map_size_pix=512,
    )
    center_lat, center_lon = get_center_coord_by_area_size(coords)

    m = create_base_map(
        center_latlon=(center_lat, center_lon),
        start_zoom_level=start_zoom_level,
    )

    lat, lon = coords.pop(0)
    folium.Marker(
        [lat, lon],
        icon=folium.plugins.BeautifyIcon(background_color="#888", icon="car", border_width=1),
    ).add_to(m)

    pre_lat = lat
    pre_lon = lon
    while(coords):
        lat, lon = coords.pop(0)
        folium.Marker(
            [lat, lon],
            icon=folium.plugins.BeautifyIcon(background_color="#888", icon="car", border_width=1),
        ).add_to(m)

        # polyline_point_moved = folium.PolyLine(
        #     [[[pre_lat, pre_lon], [lat, lon]]],
        #     color="#f4a460",
        # ).add_to(m)
        # polyline_textpath_attr = {"fill": "#000000", "font-weight": "bold", "font-size": "20"}
        # folium.plugins.PolyLineTextPath(
        #     polyline_point_moved,
        #     ">",
        #     repeat=True,
        #     offset=7,
        #     attributes=polyline_textpath_attr,
        # ).add_to(m)

        _, _, distance_2points = geod.inv(pre_lon, pre_lat, lon, lat)
        folium.Marker(
            [pre_lat + (lat - pre_lat)/2, pre_lon + (lon - pre_lon)/2],
            icon=folium.DivIcon(html=f"<b><font size='3'>{distance_2points:.1f}m</font></b>"),
        ).add_to(m)

        pre_lat = lat
        pre_lon = lon

    return m
