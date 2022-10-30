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


def create_map_display_base_point_moving(
        base_point_lat: float,
        base_point_lon: float,
        base_point_direction_degree: float,
        moved_point_lat: float,
        moved_point_lon: float,
        rel_dist_depth_metre: float,
        rel_dist_width_metre: float,
        rel_dist_height_metre: Optional[float]=None,
    ) -> "folium.Map":
    # base_point -> target_point
    depth_lon, depth_lat ,_ = geod.fwd(base_point_lon, base_point_lat, base_point_direction_degree, rel_dist_depth_metre)
    horizon_direction_degree = (base_point_direction_degree - 90) % 360
    target_lon, target_lat ,_ = geod.fwd(depth_lon, depth_lat, horizon_direction_degree, rel_dist_width_metre)

    # moved_point -> target_point
    moved_depth_lon, moved_depth_lat ,_ = geod.fwd(moved_point_lon, moved_point_lat, base_point_direction_degree, rel_dist_depth_metre)
    moved_target_lon, moved_target_lat ,_ = geod.fwd(moved_depth_lon, moved_depth_lat, horizon_direction_degree, rel_dist_width_metre)

    coords = [
        (base_point_lat, base_point_lon),
        (depth_lat, depth_lon),
        (target_lat, target_lon),
        (moved_point_lat, moved_point_lon),
        (moved_depth_lat, moved_depth_lon),
        (moved_target_lat, moved_target_lon),
    ]

    map_center_lat, map_center_lon = get_center_coord_by_area_size(coords)

    start_zoom_level = adjust_zoom_level(
        left_top_latlon=get_lefttop_coord(coords),
        right_bottom_latlon=get_rightbottom_coord(coords),
        width_map_size_pix=512,
        height_map_size_pix=512,
    )

    m = create_base_map(
        center_latlon=[map_center_lat, map_center_lon],
        start_zoom_level=start_zoom_level,
    )

    # base_point関連の描画.
    folium.Marker(
        [base_point_lat, base_point_lon],
        icon=folium.plugins.BeautifyIcon(background_color="#888", icon="car", border_width=1),
    ).add_to(m)
    folium.Marker(
        [target_lat, target_lon],
        # popup=folium.Popup(f"{10.0}m", show=True),
        icon=folium.plugins.BeautifyIcon(background_color="#888", border_width=1),
    ).add_to(m)
    folium.PolyLine(
        [[[base_point_lat, base_point_lon], [depth_lat, depth_lon]], [[depth_lat, depth_lon], [target_lat, target_lon]]],
        color="#444",
    ).add_to(m)

    # moved_point関連の描画.
    folium.Marker(
        [moved_point_lat, moved_point_lon],
        icon=folium.plugins.BeautifyIcon(background_color="#fc6", icon="car", border_width=1),
    ).add_to(m)
    folium.Marker(
        [moved_target_lat, moved_target_lon],
        # popup=folium.Popup(f"{10.0}m", show=True),
        icon=folium.plugins.BeautifyIcon(background_color="#fc6", border_width=1),
    ).add_to(m)
    folium.PolyLine(
        [[[moved_point_lat, moved_point_lon], [moved_depth_lat, moved_depth_lon]], [[moved_depth_lat, moved_depth_lon], [moved_target_lat, moved_target_lon]]],
    ).add_to(m)
    folium.Marker(
        [moved_depth_lat + (moved_point_lat - moved_depth_lat)/2, moved_depth_lon + (moved_point_lon - moved_depth_lon)/2],
        icon=folium.DivIcon(html=f"<b><font size='3'>depth:{rel_dist_depth_metre:.1f}m</font></b>"),
    ).add_to(m)
    folium.Marker(
        [moved_depth_lat + (moved_target_lat - moved_depth_lat)/2, moved_depth_lon + (moved_target_lon - moved_depth_lon)/2],
        icon=folium.DivIcon(html=f"<b><font size='3'>width:{rel_dist_width_metre:.1f}m</font></b>"),
    ).add_to(m)
    if rel_dist_height_metre is not None:
        folium.Marker(
            [moved_target_lat, moved_target_lon],
            icon=folium.DivIcon(html=f"<b><font size='3'>height:{rel_dist_height_metre:.1f}m</font></b>"),
        ).add_to(m)

    polyline_base2moved = folium.PolyLine(
        [[[base_point_lat, base_point_lon], [moved_point_lat, moved_point_lon]]],
        color="#f4a460",
    ).add_to(m)
    polyline_textpath_attr = {"fill": "#000000", "font-weight": "bold", "font-size": "20"}
    folium.plugins.PolyLineTextPath(
        polyline_base2moved,
        ">",
        repeat=True,
        offset=7,
        attributes=polyline_textpath_attr,
    ).add_to(m)

    return m
