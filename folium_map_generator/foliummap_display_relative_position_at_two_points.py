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


def create_map_display_relative_position_at_two_points(
        base_point_lat: float,
        base_point_lon: float,
        base_point_direction_degree: float,
        rel_dist_depth_metre: float,
        rel_dist_width_metre: float,
        rel_dist_height_metre: Optional[float]=None,
    ) -> "folium.Map":
    depth_lon, depth_lat ,_ = geod.fwd(base_point_lon, base_point_lat, base_point_direction_degree, rel_dist_depth_metre)
    horizon_direction_degree = (base_point_direction_degree - 90) % 360
    target_lon, target_lat ,_ = geod.fwd(depth_lon, depth_lat, horizon_direction_degree, rel_dist_width_metre)
    coords = [
        (base_point_lat, base_point_lon),
        (depth_lat, depth_lon),
        (target_lat, target_lon),
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

    folium.Marker(
        [base_point_lat, base_point_lon],
        icon=folium.plugins.BeautifyIcon(background_color="#fc6", icon="car", border_width=1),
    ).add_to(m)
    folium.Marker(
        [target_lat, target_lon],
        # popup=folium.Popup(f"{10.0}m", show=True),
        icon=folium.plugins.BeautifyIcon(background_color="#fc6", border_width=1),
    ).add_to(m)
    folium.PolyLine(
        [[[base_point_lat, base_point_lon], [depth_lat, depth_lon]], [[depth_lat, depth_lon], [target_lat, target_lon]]],
    ).add_to(m)
    folium.Marker(
        [depth_lat + (base_point_lat - depth_lat)/2, depth_lon + (base_point_lon - depth_lon)/2],
        icon=folium.DivIcon(html=f"<b><font size='3'>depth:{rel_dist_depth_metre:.1f}m</font></b>"),
    ).add_to(m)
    folium.Marker(
        [depth_lat + (target_lat - depth_lat)/2, depth_lon + (target_lon - depth_lon)/2],
        icon=folium.DivIcon(html=f"<b><font size='3'>width:{rel_dist_width_metre:.1f}m</font></b>"),
    ).add_to(m)
    if rel_dist_height_metre is not None:
        folium.Marker(
            [target_lat, target_lon],
            icon=folium.DivIcon(html=f"<b><font size='3'>height:{rel_dist_height_metre:.1f}m</font></b>"),
        ).add_to(m)
    return m




# def create_map_with_some_coords(
#         coords: list[tuple[float, float]],
#     ) -> "folium.Map":
#     if not coords:
#         raise
#     start_zoom_level = adjust_zoom_level(
#         left_top_latlon=get_lefttop_coord(coords),
#         right_bottom_latlon=get_rightbottom_coord(coords),
#         width_map_size_pix=512,
#         height_map_size_pix=512,
#     )
#     center_lat, center_lon = get_center_coord_by_area_size(coords)
# 
#     m = create_base_map(
#         center_latlon=[center_lat, center_lon],
#         start_zoom_level=start_zoom_level,
#     )
# 
#     for lat, lon in coords:
#         pass
