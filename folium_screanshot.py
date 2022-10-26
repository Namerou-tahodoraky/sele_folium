import os
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import folium
import folium.plugins
from io import BytesIO
from PIL import Image
import tempfile
import uuid
import numpy as np
import pyproj


def screenshot(driver) -> bytes:
    # w = driver.execute_script('return document.body.scrollWidth')
    # h = driver.execute_script('return document.body.scrollHeight')
    w = 650 # 小さくしすぎるとスクロールバーが表示されてしまう.
    h = 650 # 小さくしすぎるとスクロールバーが表示されてしまう.
    driver.set_window_size(w, h)
    image_binary = BytesIO(driver.get_screenshot_as_png())
    return image_binary


def valid_image_loaded(
        image_pil,
        squer_size: int=50,
        split_num: int=10,
        disable_pixvalue_ranges=None,
        # min_pixvalue_thresh=245,
        # max_pixvalue_thresh=256,
        min_disable_pixratio_thresh: float=0.8,
    ) -> bool:
    assert(squer_size % split_num == 0), f"ArgmentValueError: squer_size and split_num must be according to the expresion, squer_size % split_num == 0."
    if not disable_pixvalue_ranges:
        disable_pixvalue_ranges = [(215, 225), (245, 256)]
    onegrid_pix_num = int(squer_size / split_num)

    image_loaded_flag = True
    a = np.array(image_pil.convert('L').resize((squer_size, squer_size)))
    a = np.array(np.array_split(a, split_num, axis=1))
    a = a.reshape(-1, onegrid_pix_num * onegrid_pix_num)
    # a = np.vstack((a[0:onegrid_pix_num], a[-onegrid_pix_num:]))

    for min_pixvalue_thresh, max_pixvalue_thresh in disable_pixvalue_ranges:
        tmp = ((min_pixvalue_thresh < a) * (a <= max_pixvalue_thresh)).mean(axis=1)
        image_loaded_flag = np.all(tmp < min_disable_pixratio_thresh)
        if not image_loaded_flag:
            break
    return image_loaded_flag


if __name__ == '__main__':
    c_lat, c_lon = [34.841023, 137.3243984]
    geod = pyproj.Geod(ellps="WGS84")
    d_metre = 200
    d_degree = 45
    d_lon, d_lat ,_ = geod.fwd(c_lon, c_lat, d_degree, d_metre)
    w_metre = 400
    h_metre = 18.333333333
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
    folium.Marker(
        [p_lat, p_lon],
        icon=folium.DivIcon(html=f"<b><font size='3'>height:{h_metre:.1f}m</font></b>"),
    ).add_to(m)

    # bounds = m.get_bounds()
    # print(bounds)
    # _, _, bounds_w_metre = geod.inv(bounds[0][1], bounds[0][0], bounds[1][1], bounds[0][0])
    # _, _, bounds_h_metre = geod.inv(bounds[0][1], bounds[0][0], bounds[0][1], bounds[1][0])
    # print(bounds_w_metre, bounds_h_metre)
    # m.fit_bounds(
    #     # [[34.841408, 137.323999], [34.840767, 137.325260]],
    #     [[34.8413, 137.322], [34.840767, 137.325260]],
    #     # max_zoom=22, # TileLayerで指定されていれば必要ない.
    # )

    html_path = f"./html/{uuid.uuid4()}.html"
    m.save(html_path)

    driver = webdriver.Remote(
        command_executor='http://localhost:4444/wd/hub',
        options=webdriver.ChromeOptions(),
    )

    driver.implicitly_wait(3)

    selenium_html_path = f"file:///share/{os.path.basename(html_path)}"
    ## get website
    try:
        for n in range(1):
            image_name = f"{os.path.splitext(os.path.basename(html_path))[0]}_{n:03}.png"
            image_path = os.path.join("images2", image_name)

            wait_time = 0.0
            wait_time_range = 0.3
            image_loaded_flag = False
            max_repeat_num = 5
            repeat_num = 0
            while(not image_loaded_flag and repeat_num < max_repeat_num):
                print(repeat_num)
                driver.get(selenium_html_path)

                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "folium-map")))
                time.sleep(wait_time)

                image_pil = Image.open(screenshot(driver)).crop((0, 0, 500, 500))

                image_loaded_flag = valid_image_loaded(image_pil)
                wait_time += wait_time_range
                repeat_num += 1

            if image_loaded_flag:
                image_pil.save(image_path)
            else:
                print("Not loaded!!!")
                image_pil.save(image_path)

    except WebDriverException as e:
        print(e)
    finally:
        driver.quit()
        os.remove(html_path)

