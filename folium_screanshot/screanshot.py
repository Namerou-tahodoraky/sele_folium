from __future__ import annotations
import os
from typing import Optional
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from io import BytesIO
from PIL import Image
import numpy as np

from typing import Optional
from folium import Map
from PIL.Image import Image as ImageInstance


class AirialImageRenderBySelenium:
    def __init__(self,
        selenium_server_adress: str,
        share_dir_path_in_this_server: str,
        share_dir_abspath_in_selenium_server: str,
    ) -> None:
        html_filename = "tmp.html"

        self.html_path_in_this_server = os.path.join(share_dir_path_in_this_server, html_filename)
        self.html_abspath_in_selenium_server = os.path.join(f"file://{share_dir_abspath_in_selenium_server}", html_filename)

        driver = webdriver.Remote(
            command_executor=selenium_server_adress,
            options=webdriver.ChromeOptions(),
        )
        driver.implicitly_wait(3)
        self.driver = driver

    def __del__(self) -> None:
        driver = self.driver
        html_path_in_this_server = self.html_path_in_this_server

        driver.quit()
        if os.path.isfile(html_path_in_this_server):
            os.remove(html_path_in_this_server)

    def send_html_to_selenium_server(self, wait_time: int=0) -> None:
        driver = self.driver
        html_abspath_in_selenium_server = self.html_abspath_in_selenium_server

        driver.get(html_abspath_in_selenium_server)
        try:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "folium-map")))
        except TimeoutException as e:
            print("Error: please check shared directory path.")
            raise e
        time.sleep(wait_time)

    def get_image_from_selenium_server(self) -> "ImageInstance":
        driver = self.driver
        # w = driver.execute_script('return document.body.scrollWidth')
        # h = driver.execute_script('return document.body.scrollHeight')
        w = 650 # 小さくしすぎるとスクロールバーが表示されてしまう.
        h = 650 # 小さくしすぎるとスクロールバーが表示されてしまう.
        driver.set_window_size(w, h)
        image_binary = BytesIO(driver.get_screenshot_as_png())
        image_pil = Image.open(image_binary).crop((0, 0, 512, 512))
        return image_pil

    def valid_image_loaded(
            self,
            image_pil,
            squer_size: int=50,
            split_num: int=10,
            disable_pixvalue_ranges=None,
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

        for min_pixvalue_thresh, max_pixvalue_thresh in disable_pixvalue_ranges:
            tmp = ((min_pixvalue_thresh < a) * (a <= max_pixvalue_thresh)).mean(axis=1)
            image_loaded_flag = np.all(tmp < min_disable_pixratio_thresh)
            if not image_loaded_flag:
                break
        return image_loaded_flag

    def render(self,
            folium_map: "Map",
    ) -> Optional["Image"]:
        html_path_in_this_server = self.html_path_in_this_server
        folium_map.save(html_path_in_this_server)

        wait_time = 0.0
        wait_time_range = 0.3
        image_loaded_flag = False
        max_repeat_num = 5
        repeat_num = 0
        image_pil = None
        while(not image_loaded_flag and repeat_num < max_repeat_num):
            self.send_html_to_selenium_server(wait_time=wait_time)
            image_pil = self.get_image_from_selenium_server()
            image_loaded_flag = self.valid_image_loaded(image_pil)
            wait_time += wait_time_range
            repeat_num += 1

        if not image_loaded_flag:
            image_pil = None
            print("Not loaded!!!")

        return image_pil
