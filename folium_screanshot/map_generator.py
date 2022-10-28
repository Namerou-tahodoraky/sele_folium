
import folium
import folium.plugins
import pyproj
from typing import Optional


geod = pyproj.Geod(ellps="WGS84")


def create_map_with_relative_distance_from_camera(
        c_lat: float,
        c_lon: float,
        d_degree: float,
        d_metre: float,
        w_metre: float,
        h_metre: Optional[float]=None,
    ) -> "folium.Map":
    d_lon, d_lat ,_ = geod.fwd(c_lon, c_lat, d_degree, d_metre)
    w_degree = (d_degree - 90) % 360
    p_lon, p_lat ,_ = geod.fwd(d_lon, d_lat, w_degree, w_metre)
    mc_lat, mc_lon = c_lat + (p_lat - c_lat)/2.0, c_lon + (p_lon - c_lon)/2.0
    start_zoom_level = 21 - int(max(d_metre, w_metre) / 20) # zoom_level=21の時, 直角方向の距離で20mなら十分マップ内に入る.30mだと入らない.
    start_zoom_level = max(16, start_zoom_level)

    m = folium.Map(
        location=[mc_lat, mc_lon], # fit_boundsを指定する場合はlocationは記述しない.
        zoom_start=start_zoom_level, #TileLayerではなくMap側で指定する.
        tiles=None, # TileLayerで指定したタイルをデフォルト表示にする為に必要
        zoom_control=False, # 左上のzoom_levelを操作するボタン(+,-)が消える.
        control_scale=True, # 左下にメートルバーが追加される.
        no_touch=True, # 意味があるかは不明.
        # disable_3d=True, # zoom_levelの指定が変になる.タイルの取得が遅くなる.
        width=500,
        height=500,
    )

    folium.TileLayer(
        tiles='https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg',
        attr=" ", # tilesにurlを指定した場合は何かしらの文字列が必須.
        max_native_zoom=18, # タイル標準のzoom_levelを超える場合は必須.
        max_zoom=22, # タイル標準のzoom_levelを超える場合は必須.
        overlay=True, # TileLayerで指定したタイルをデフォルト表示にする為に必要,
        control=False, # 意味があるかは不明.
    ).add_to(m)
    folium.Marker(
        [c_lat, c_lon],
        icon=folium.plugins.BeautifyIcon(background_color="#fc6", icon="car", border_width=1),
    ).add_to(m)
    folium.Marker(
        [p_lat, p_lon],
        # popup=folium.Popup(f"{10.0}m", show=True),
        icon=folium.plugins.BeautifyIcon(background_color="#fc6", border_width=1),
    ).add_to(m)
    folium.PolyLine(
        [[[c_lat, c_lon], [d_lat, d_lon]], [[d_lat, d_lon], [p_lat, p_lon]]],
    ).add_to(m)
    folium.Marker(
        [d_lat + (c_lat - d_lat)/2, d_lon + (c_lon - d_lon)/2],
        icon=folium.DivIcon(html=f"<b><font size='3'>depth:{d_metre:.1f}m</font></b>"),
    ).add_to(m)
    folium.Marker(
        [d_lat + (p_lat - d_lat)/2, d_lon + (p_lon - d_lon)/2],
        icon=folium.DivIcon(html=f"<b><font size='3'>width:{w_metre:.1f}m</font></b>"),
    ).add_to(m)
    if h_metre is not None:
        folium.Marker(
            [p_lat, p_lon],
            icon=folium.DivIcon(html=f"<b><font size='3'>height:{h_metre:.1f}m</font></b>"),
        ).add_to(m)
    return m

