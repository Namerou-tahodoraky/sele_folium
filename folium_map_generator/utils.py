import folium
# import folium.plugins
# import pyproj
from typing import Union
import numpy as np

# geod = pyproj.Geod(ellps="WGS84")

def adjust_zoom_level(
    left_top_latlon: tuple[float, float],
    right_bottom_latlon: tuple[float, float],
    width_map_size_pix: Union[int, float],
    height_map_size_pix: Union[int, float],
    ) -> int:
    lt_lat, lt_lon = left_top_latlon
    rb_lat, rb_lon = right_bottom_latlon
    max_zoom_level = 22
    min_zoom_level = 0
    L = 85.05112878

    coords = np.array([
        [lt_lat, lt_lon],
        [rb_lat, rb_lon],
    ])

    now_zoom_level = max_zoom_level
    while(now_zoom_level > min_zoom_level):
        # 緯度 -> タイル内のX軸ピクセル座標
        x_pixs = (2 ** (now_zoom_level+7)) * (coords[:, 0] / 180.0 + 1)
        x_vis_area_size_pix = x_pixs[1] - x_pixs[0]

        # 経度 -> タイル内のY軸ピクセル座標
        y_pixs = ((2 ** (now_zoom_level+7)) / np.pi) * (
            -np.arctanh(np.sin(coords[:, 1] * np.pi/180.0))
            + -np.arctanh(np.sin(L * np.pi/180.0))
        )
        y_vis_area_size_pix = y_pixs[1] - y_pixs[0]

        if (x_vis_area_size_pix < width_map_size_pix) and (y_vis_area_size_pix < height_map_size_pix):
            break
        now_zoom_level -= 1
    return now_zoom_level


def get_lefttop_coord(coords: list[tuple[float, float]]) -> tuple[float, float]:
    coords = np.array(coords)
    return np.min(coords, axis=0)


def get_rightbottom_coord(coords: list[tuple[float, float]]) -> tuple[float, float]:
    coords = np.array(coords)
    return np.max(coords, axis=0)


def get_center_coord_by_median(coords: list[tuple[float, float]]) -> tuple[float, float]:
    coords = np.array(coords)
    return np.mean(coords, axis=0)


def get_center_coord_by_area_size(coords: list[tuple[float, float]]) -> tuple[float, float]:
    coords = np.array(coords)
    lt_coord = get_lefttop_coord(coords)
    rb_coord = get_rightbottom_coord(coords)
    coords = np.array([
        lt_coord,
        rb_coord,
    ])
    return np.mean(coords, axis=0)


def create_base_map(
        center_latlon: tuple[float, float],
        start_zoom_level: float,
    ) -> "folium.Map":
    center_lat, center_lon = center_latlon
    m = folium.Map(
        location=[center_lat, center_lon], # fit_boundsを指定する場合はlocationは記述しない.
        zoom_start=start_zoom_level, #TileLayerではなくMap側で指定する.
        tiles=None, # TileLayerで指定したタイルをデフォルト表示にする為に必要
        zoom_control=False, # 左上のzoom_levelを操作するボタン(+,-)が消える.
        control_scale=True, # 左下にメートルバーが追加される.
        no_touch=True, # 意味があるかは不明.
        # disable_3d=True, # zoom_levelの指定が変になる.タイルの取得が遅くなる.
        width=512,
        height=512,
    )
    folium.TileLayer(
        tiles='https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg',
        attr=" ", # tilesにurlを指定した場合は何かしらの文字列が必須.
        max_native_zoom=18, # タイル標準のzoom_levelを超える場合は必須.
        max_zoom=22, # タイル標準のzoom_levelを超える場合は必須.
        overlay=True, # TileLayerで指定したタイルをデフォルト表示にする為に必要,
        control=False, # 意味があるかは不明.
    ).add_to(m)
    return m

